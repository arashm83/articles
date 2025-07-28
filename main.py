from fastapi import FastAPI, WebSocket, Request, Form, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cores.auth import decode_token, create_access_token, verify_password
from cores.db_manager import DbManager, User, engine, Base, get_db

Base.metadata.create_all(bind=engine)
app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount('/statics', StaticFiles(directory='statics'), name='statics')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    token = request.cookies.get("access_token")
    payload = decode_token(token) if token else None
    username = payload.get("sub") if payload else None

    if not username:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: DbManager = Depends(get_db)):
    if db.get_user(username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "This username is already taken."})
    db.create_user(username, password)
    return RedirectResponse("/login", status_code=303)

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: DbManager = Depends(get_db)):
    user = db.get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."})
    token = create_access_token({"sub": username})
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("access_token", token, httponly=True)
    return response

@app.get("/api/articles")
def get_articles(request: Request, db: DbManager = Depends(get_db)):
    articles = db.get_all_articles()
    return [{
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "abstract": article.abstract,
        "pdf_url" : article.pdf_url,
        "created_at": article.create_at.isoformat(),
    } for article in articles]


connected_websockets: list[WebSocket] = []
@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)

async def notify_new_article(connected_websockets, title: str):
    print(connected_websockets)
    for ws in connected_websockets:
        try:
            await ws.send_text(f"new article : {title}")
        except:
            pass


@app.post('/article')
async def notify(request: Request):
    title = request.headers.get('title')
    await notify_new_article(connected_websockets, title)
    return {"title": title}

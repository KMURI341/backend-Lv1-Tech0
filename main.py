from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db  # 絶対インポート
from backend.models import MProductMurai as Product, TransactionMurai as Transaction, TransactionDetailsMurai as TransactionDetail  # 絶対インポート
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CORS 設定（Next.js からのリクエストを許可）
app.add_middleware( CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=True, allow_methods=[""], allow_headers=[""], )

# 初回起動時にテーブルを作成
Base.metadata.create_all(bind=engine)

# ✅ `/hello` エンドポイント（Next.js の GET 用）
@app.get("/hello")
def read_root():
    return {"message": "Hello from FastAPI"}

# ✅ `/multiply/{number}` エンドポイント（Next.js の ID指定 GET 用）
@app.get("/multiply/{number}")
def multiply_number(number: int):
    return {"doubled_value": number * 2}

# ✅ `/echo` エンドポイント（Next.js の POST 用）
class EchoMessage(BaseModel):
    message: str

@app.post("/echo")
def echo_message(payload: EchoMessage):
    return {"message": f"受信したメッセージ: {payload.message}"}

# 既存の `GET /products/{product_code}`
@app.get("/products/{product_code}")
def get_product(product_code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.code == product_code).first()
    if product is None:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return product

# 既存の `POST /products/`
@app.post("/products/")
def create_product(code: str, name: str, price: float, db: Session = Depends(get_db)):
    new_product = Product(code=code, name=name, price=price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# ✅ 購入リスト管理用のエンドポイント（仮の実装）
cart = []  # 購入リスト

# ✅ カートに商品を追加
@app.post("/cart/add/{product_code}")
def add_to_cart(product_code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.code == product_code).first()
    if product is None:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    cart.append(product)
    return {"message": f"{product.name} をカートに追加しました", "cart": cart}

# ✅ カートの中身を取得
@app.get("/cart/")
def get_cart():
    return {"cart": cart}

# ✅ カートの合計金額を計算
@app.get("/cart/total")
def get_cart_total():
    total_price = sum(item.price for item in cart)
    return {"total_price": total_price}

# ✅ 取引を作成するエンドポイント
class CartItem(BaseModel):
    product_code: str
    quantity: int

class TransactionCreate(BaseModel):
    cart_items: List[CartItem]

@app.post("/transactions/")
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    total_amount = 0.0
    # カート内商品の合計金額を計算
    for item in payload.cart_items:
        product = db.query(Product).filter(Product.code == item.product_code).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品 {item.product_code} が見つかりません")
        total_amount += float(product.price) * item.quantity

    # 取引を作成
    new_transaction = Transaction(
        total_amount=total_amount
        # 必要なら、cashier_code, store_code, pos_id などを設定
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # 取引明細を作成
    for item in payload.cart_items:
        product = db.query(Product).filter(Product.code == item.product_code).first()
        new_detail = TransactionDetail(
            transaction_id=new_transaction.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(new_detail)
    db.commit()

    return {
        "transaction_id": new_transaction.id,
        "total_amount": new_transaction.total_amount,
        "message": "取引が完了しました"
    }

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from backend.database import Base



# 商品マスタ（m_product_murai）
class MProductMurai(Base):
    __tablename__ = "m_product_murai"  # 新しいテーブル名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)

# 取引（transaction_murai）
class TransactionMurai(Base):
    __tablename__ = "transaction_murai"  # 新しいテーブル名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_date = Column(DateTime, default=func.now())
    cashier_code = Column(String(20), default='9999999999')
    store_code = Column(String(10), default='30')
    pos_id = Column(String(10), default='90')
    total_amount = Column(DECIMAL(10,2), default=0)

# 取引明細（transaction_details_murai）
class TransactionDetailsMurai(Base):
    __tablename__ = "transaction_details_murai"  # 新しいテーブル名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transaction_murai.id"), nullable=False)  # 取引IDを外部キーに設定
    product_id = Column(Integer, ForeignKey("m_product_murai.id"), nullable=False)  # 商品IDを外部キーに設定
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(DECIMAL(10,2), nullable=False)

    # リレーション
    transaction = relationship("TransactionMurai")
    product = relationship("MProductMurai")

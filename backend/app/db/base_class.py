from sqlalchemy.ext.declarative import declarative_base, declared_attr

class CustomBase:
    # 可以为所有表自动生成 __tablename__
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

# 使用我们自定义的基类创建 Declarative Base
Base = declarative_base(cls=CustomBase) 
# from sqlalchemy import String,ForeignKey,JSON,Integer,DateTime,Boolean
# from sqlalchemy.orm import Mapped,MappedColumn
# from datetime import datetime,timezone
# from app.core.database import Base


# class ConsentRecord(Base):
#     __tablename__ = "consent_records"

#     id : Mapped[int] = MappedColumn (
#         Integer,
#         primary_key = True,
#         index = True
#     )
#     user_id : Mapped[int]  = MappedColumn (
#         ForeignKey("users.id"),
#     )
#     tenant_id : Mapped[int | None] = MappedColumn (
#         ForeignKey("tenants.id"),
#         nullable = True
#     )
#     consent_type :Mapped[str] = MappedColumn (
#         String,
#         nullable = False
#     )
#     accepted : Mapped[bool] = MappedColumn (
#         Boolean,
#         default = True
#     )
#     version : Mapped[str]  = MappedColumn (
#         String,
#         default = "v1"
#     )
#     ip_address: Mapped[str] = MappedColumn (
#         String,
#         nullable = True
#     )
#     accepted_at: Mapped[datetime] = MappedColumn (
#         DateTime,
#         default = datetime.now(timezone.utc)
#     )
#     revoked_at : Mapped[datetime] = MappedColumn (
#         DateTime,
#         nullable = True
#     )

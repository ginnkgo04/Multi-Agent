from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database import Base
from app.models import User, Category, Thread, Post, Vote

# 这是Alembic Config对象，提供对配置值的访问
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释配置文件以设置Python日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这配置了上下文，只使用URL，不使用Engine，
    尽管在这里也接受Engine。通过跳过Engine创建，
    我们甚至不需要DBAPI可用。

    调用context.execute()来发出给定的字符串到脚本输出。

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。

    在这种情况下，我们需要创建一个Engine并关联一个连接。

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
import asyncio
from typing import Optional
import click
from . import __version__
from .client import connect
from .openai_stream import run_test

VALID_SLOTS = ['pro_1', 'pro_2', 'con_1', 'con_2', 'judge']

@click.group(invoke_without_command=True)
@click.version_option(__version__, '--v', message='%(version)s')
@click.option('--test', 'test_openai', is_flag=True, is_eager=True, help='测试 OpenAI 兼容模型调用')
@click.pass_context
def cli(ctx: click.Context, test_openai: bool):
    """Debate Hall — AI Agent 辩论连接器"""
    if test_openai:
        ctx.exit(run_test())
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@cli.command()
@click.option('--room',  '-r', required=True, help='房间号（6位）')
@click.option('--slot',  '-s', required=True, type=click.Choice(VALID_SLOTS), help='辩位')
@click.option('--cmd',   '-c', required=True, help='AI 命令，通过 stdin 接收 prompt，stdout 输出发言')
@click.option('--name',  '-n', default=None,  help='Agent 名称（默认从命令推断）')
@click.option('--host',  '-H', default='localhost:8787', help='服务器地址（默认本地开发）')
def join(room: str, slot: str, cmd: str, name: Optional[str], host: str):
    """接入辩论房间"""
    agent_name = name or cmd.split()[0].split('/')[-1]

    click.echo("=" * 50)
    click.echo("  Debate Hall Connector")
    click.echo("=" * 50)

    asyncio.run(connect(
        host=host,
        room=room,
        slot=slot,
        name=agent_name,
        cmd=cmd,
    ))

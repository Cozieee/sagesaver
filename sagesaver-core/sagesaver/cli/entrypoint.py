import click

from .entityconfig import EntityConfiguration

@click.group()
def main():
    pass

@main.group()
@click.option('--region', required=True, prompt = True)
@click.option('--stack-name', required=True, prompt = True)
@click.pass_context
def configure(ctx, stack_name, region):
    ctx.ensure_object(dict)
    ctx.obj['stack_name'] = stack_name
    ctx.obj['region'] = region

@configure.result_callback()
def save_configuration(cfg: EntityConfiguration, **_):
    cfg.save_environmentals()

@configure.command(name = "user")
@click.pass_context
def install_user(ctx):
    cfg = EntityConfiguration(**ctx.obj, entity_type = "user")
    return cfg

@configure.command(name = "mysql")
@click.pass_context
def install_mysql(ctx, username, password):
    cfg = EntityConfiguration(**ctx.obj, entity_type = "mysql")
    cfg.install(username = username, password = password)
    return cfg


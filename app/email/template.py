from jinja2 import Environment, FileSystemLoader
from app.core.config import BASE_DIR

env = Environment(
    loader=FileSystemLoader(BASE_DIR / 'app/templates')
)

def render_template(template_name: str, context: dict) -> str:

    if not template_name.endswith('.html'):
        template_name = f"{template_name}.html"

    template = env.get_template(template_name)
    return template.render(**context)
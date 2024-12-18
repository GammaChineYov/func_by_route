# product_module.py
from blueprint import Blueprint

product_blueprint = Blueprint("product", url_prefix="/product")

@product_blueprint.route("/<int:id>", methods=["GET"])
def product_detail(id):
	return f"商品详情：ID = {id}"
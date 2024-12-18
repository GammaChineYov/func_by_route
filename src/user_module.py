# user_module.py
from blueprint import Blueprint

# 创建主蓝图和子蓝图
user_blueprint = Blueprint("user", url_prefix="/user")
profile_blueprint = Blueprint("profile", url_prefix="/profile")
settings_blueprint = Blueprint("settings", url_prefix="/settings")

# 注册子蓝图
user_blueprint.register_blueprint(profile_blueprint)
user_blueprint.register_blueprint(settings_blueprint)

# 定义路由
@user_blueprint.route("/", methods=["GET"])
def user_home():
	return "用户首页"

@profile_blueprint.route("/", methods=["GET"])
def profile_home():
	return "用户资料首页"

@profile_blueprint.route("/<string:username>", methods=["GET"])
def user_profile(username):
	return f"用户资料：{username}"

@settings_blueprint.route("/", methods=["GET"])
def settings_home():
	return "用户设置首页"

@user_blueprint.route("/back", methods=["POST"])
def user_back():
	return "回退到用户模块首页"
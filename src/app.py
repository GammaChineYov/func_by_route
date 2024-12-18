# app.py
from route_manager import RouteManager
from user_module import user_blueprint
from blueprint import Blueprint

# 主蓝图
app = Blueprint("app")

# 子蓝图
user_blueprint = Blueprint("user", url_prefix="/user")
profile_blueprint = Blueprint("profile", url_prefix="/profile")
settings_blueprint = Blueprint("settings", url_prefix="/settings")

# 注册路由
@user_blueprint.route("/")
def user_home():
	return "User Home"

@user_blueprint.route("/back")
def user_back():
	return "User Back"

@profile_blueprint.route("/")
def profile_home():
	return "Profile Home"

@profile_blueprint.route("/<string:username>")
def user_profile(username):
	return f"Profile of {username}"

@settings_blueprint.route("/")
def settings_home():
	return "Settings Home"

# 注册子蓝图
user_blueprint.register_blueprint(profile_blueprint)
user_blueprint.register_blueprint(settings_blueprint)
app.register_blueprint(user_blueprint)

# 注册主路由
app.register_routes(app.url_map, app.view_functions)

# 测试路由请求
print(app.dispatch_request("/user/settings/2"))  # User Home
print(app.dispatch_request("/user/profile/"))  # Profile Home
print(app.dispatch_request("/user/profile/john"))  # Profile of john
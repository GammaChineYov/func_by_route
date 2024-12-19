
import sys
import os
# ./
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import unittest
from werkzeug.routing import Map, Rule
from blueprint import Blueprint

class TestBlueprint(unittest.TestCase):

	def setUp(self):
		"""
		测试环境准备
		创建蓝图、路由和注册
		"""
		# 创建主蓝图和用户蓝图
		self.app = Blueprint(name="app", url_prefix="")
		self.user_bp = Blueprint(name="user", url_prefix="/user")

		# 注册路由
		@self.app.route("/")
		def app_home():
			return "App Home"

		@self.user_bp.route("/")
		def user_home():
			return "User Home"

		@self.user_bp.route("/profile/<string:username>")
		def user_profile(username):
			return f"Profile Page of {username}"

		@self.user_bp.route("/back")
		def user_back():
			return "User Back Route"

		# 注册子蓝图
		self.app.register_blueprint(self.user_bp)

		self.app.register_routes(self.app.url_map, self.app.view_functions)

		# 清空请求栈
		self.app.request_stack.clear()

	def test_relative_request(self):
		"""
		测试 relative_request 方法
		"""
		self.app.request_stack.append("/user/")
		self.app.request_stack.append("/user/profile/john")

		result = self.user_bp.relative_request("/user/profile/jane")
		self.assertEqual(result, "Profile Page of jane")

	def test_back(self):
		"""
		测试 back 方法
		"""
		self.app.request_stack.append("/user/")
		self.app.request_stack.append("/user/profile/john")

		result = self.user_bp.back()
		self.assertEqual(result, "User Back Route")

	def test_route_registration(self):
		"""
		测试路由是否正确注册
		"""
		routes = [rule.rule for rule in self.main_map.iter_rules()]
		self.assertIn('/user/', routes)
		self.assertIn('/user/profile/<string:username>', routes)
		self.assertIn('/user/back', routes)

	def test_is_rule_registered(self):
		"""
		测试 is_rule_registered 方法
		"""
		rule = Rule("/user/", methods=["GET"], endpoint="user.user_home")
		registered = self.app.is_rule_registered(rule, self.app.url_map)
		self.assertTrue(registered)

if __name__ == "__main__":
	unittest.main()

# blueprint.py
from werkzeug.routing import Map, Rule
from collections import deque
import os

def is_rule_registered(rule, main_map):
	"""
	检查规则是否已经在主路由映射中注册
	"""
	for r in main_map.iter_rules():
		if r.rule == rule.rule and r.endpoint == rule.endpoint:
			return True
	return False
	
class Blueprint:
	"""
	自定义 Blueprint 类，支持嵌套路由和相对请求
	"""
	def __init__(self, name, url_prefix=None):
		self.name = name
		self.url_prefix = url_prefix or ""
		self.url_map = Map()  # 当前蓝图的路由规则
		self.view_functions = {}  # 当前蓝图的视图函数
		self.sub_blueprints = []  # 子蓝图列表
		self.request_stack = deque()  # 路由访问记录栈

	def route(self, rule, **options):
		"""
		装饰器：注册路由
		"""
		def decorator(f):
			endpoint = f"{self.name}.{f.__name__}"
			full_rule = f"{self.url_prefix}{rule}"
			self.url_map.add(Rule(full_rule, endpoint=endpoint, **options))
			self.view_functions[endpoint] = f
			print(f"[DEBUG] 注册路由: {full_rule} -> {endpoint}")
			return f
		return decorator

	def register_blueprint(self, blueprint):
		"""
		注册子蓝图
		"""
		self.sub_blueprints.append(blueprint)
		print(f"[DEBUG] 子蓝图注册子蓝图: {blueprint.name} (当前子蓝图前缀: {blueprint.url_prefix})")
		
	def register_routes(self, main_map, main_views, parent_prefix=""):
		"""
		注册蓝图及其子蓝图的路由
		"""
		current_prefix = parent_prefix + self.url_prefix  # 当前蓝图的完整前缀
		print(f"[DEBUG] 注册子蓝图: {self.name} (前缀: {parent_prefix})")
	
		# 注册当前蓝图的路由
		for rule in self.url_map.iter_rules():
			prefixed_rule = Rule(
				parent_prefix + rule.rule,  # 路由前缀拼接
				endpoint=f"{self.name}.{rule.endpoint.split('.')[-1]}",
				methods=rule.methods,
			)
			if not is_rule_registered(prefixed_rule, main_map):  # 避免重复注册
				main_map.add(prefixed_rule)
				main_views[prefixed_rule.endpoint] = self.view_functions[rule.endpoint]
				print(f"[DEBUG] 注册路由: {parent_prefix + rule.rule} -> {self.name}.{rule.endpoint.split('.')[-1]}")
	
		# 递归注册子蓝图
		for sub_blueprint in self.sub_blueprints:
			sub_blueprint.register_routes(main_map, main_views, parent_prefix=current_prefix)
	
		print(f"[DEBUG] 注册路由完成: {self.name} (前缀: {current_prefix})")
	
	def dispatch_request(self, request_path, **kwargs):
		"""
		处理请求并匹配路由
		"""
		adapter = self.url_map.bind("")  # 创建适配器（根路径）
		try:
			# 动态匹配路由
			endpoint, args = adapter.match(request_path)
			print(f"[DEBUG] 请求匹配成功: {request_path} -> {endpoint} (参数: {args})")
			return self.view_functions[endpoint](**args)
		except Exception as e:
			print(f"[DEBUG] 路由未匹配: {request_path} err:{e}")
			return "404 Not Found"
		
	def find_common_prefix(self, current_path, target_path):
		"""
		找到当前路径和目标路径的共同前缀
		"""
		current_parts = current_path.strip("/").split("/")
		target_parts = target_path.strip("/").split("/")
		common_parts = []

		for current_part, target_part in zip(current_parts, target_parts):
			if current_part == target_part:
				common_parts.append(current_part)
			else:
				break

		common_prefix = "/".join(common_parts)
		print(f"[DEBUG] 计算共同前缀: 当前路径={current_path}, 目标路径={target_path}, 共同前缀={common_prefix}")
		return common_prefix

	def relative_request(self, target_path, **kwargs):
		"""
		实现相对请求：
		- 回退到共同路由
		- 从共同路由前进到目标路径
		"""
		if not self.request_stack:
			print("[DEBUG] 路由栈为空，无法处理相对请求")
			return "No active requests to backtrack from."

		# 获取当前路径和共同路径
		current_path = self.request_stack[-1]
		common_prefix = self.find_common_prefix(current_path, target_path)

		# 回退到共同路径
		print(f"[DEBUG] 开始回退到共同路径: 当前路径={current_path}, 共同路径={common_prefix}")
		while self.request_stack and not current_path.startswith(common_prefix):
			print(f"[DEBUG] 当前路径不匹配共同路径，执行回退: {current_path}")
			self.back()
			current_path = self.request_stack[-1] if self.request_stack else ""
		
		# 从共同路径前进到目标路径
		relative_parts = target_path[len(common_prefix):].strip("/").split("/")
		print(f"[DEBUG] 从共同路径前进到目标路径: {common_prefix} -> {target_path} (路径分段: {relative_parts})")
		for part in relative_parts:
			if not part:  # 如果部分为空，跳过
				continue
			sub_path = f"/{part}"
			next_path = f"{self.url_prefix}{sub_path}"
			if next_path in [rule.rule for rule in self.url_map.iter_rules()]:
				print(f"[DEBUG] 前进到路径: {next_path}")
				return self.dispatch_request(next_path, **kwargs)

		print(f"[DEBUG] 无法解析相对路径: {target_path}")
		return f"Could not resolve relative path: {target_path}"

	def back(self, **kwargs):
		"""
		回退逻辑：调用 /back 或执行默认回退
		"""
		if not self.request_stack:
			print("[DEBUG] 路由栈为空，无法回退")
			return "No routes to backtrack."
		
		# 弹出当前路由记录
		current_path = self.request_stack.pop()
		print(f"[DEBUG] 回退路由: {current_path} (当前栈: {list(self.request_stack)})")

		# 检查是否有 /back 路由
		back_route = f"{self.url_prefix}/back"
		if back_route in [rule.rule for rule in self.url_map.iter_rules()]:
			print(f"[DEBUG] 调用 /back 路由: {back_route}")
			return self.view_functions[f"{self.name}.back"](**kwargs)
		
		# 默认回退逻辑
		print(f"[DEBUG] 默认回退逻辑: {self.name}")
		return f"Default back action for {self.name}"
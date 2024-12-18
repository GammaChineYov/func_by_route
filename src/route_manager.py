# route_manager.py
from werkzeug.routing import Map
from werkzeug.exceptions import NotFound

class RouteManager:
	"""
	主路由管理器：管理所有 Blueprint 的路由规则
	"""
	def __init__(self):
		self.url_map = Map()  # 路由规则映射表
		self.view_functions = {}  # 视图函数映射

	def register_blueprint(self, blueprint):
		"""
		注册 Blueprint
		:param blueprint: Blueprint 实例
		"""
		blueprint.register_routes(self.url_map, self.view_functions)
		
	
	
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
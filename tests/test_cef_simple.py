"""
简单的 CEF 测试 - 验证 CEF 是否能正常工作
"""
import sys

print("=" * 50)
print("CEF 简单测试")
print("=" * 50)
print(f"Python 版本: {sys.version}")
print()

# 尝试导入 CEF
try:
    print("正在导入 cefpython3...")
    from cefpython3 import cefpython as cef
    print("[成功] CEF 导入成功")
except Exception as e:
    print(f"[错误] CEF 导入失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    input("\n按回车键退出...")
    sys.exit(1)

# 尝试初始化 CEF
try:
    print("\n正在初始化 CEF...")
    settings = {
        "multi_threaded_message_loop": False,
        "log_severity": cef.LOGSEVERITY_INFO,
    }
    cef.Initialize(settings)
    print("[成功] CEF 初始化成功")
except Exception as e:
    print(f"[错误] CEF 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    input("\n按回车键退出...")
    sys.exit(1)

# 尝试创建浏览器窗口
try:
    print("\n正在创建浏览器窗口...")
    window_info = cef.WindowInfo()
    window_info.SetAsPopup(0, "CEF 测试 - 抖音")
    window_info.width = 1100
    window_info.height = 750
    
    browser = cef.CreateBrowserSync(
        window_info,
        {"javascript": "enable"},
        "https://www.douyin.com/"
    )
    print("[成功] 浏览器窗口创建成功")
    print("\n如果看到浏览器窗口，说明 CEF 工作正常！")
    print("关闭浏览器窗口后，程序将退出。")
    
    # 消息循环
    cef.MessageLoop()
    
except Exception as e:
    print(f"[错误] 创建浏览器失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n正在清理 CEF...")
    cef.Shutdown()
    print("[成功] 清理完成")

input("\n按回车键退出...")


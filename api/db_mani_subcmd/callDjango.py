class DjangoAPIBase():
    def call_django(self):
        import os
        import sys
        path = os.path.split(os.getcwd())[0]
        path = os.path.split(path)[0]
        sys.path.append(path)
        # os.system("echo $PYTHONPATH")
        # 调用django models.py必备代码段
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "ParasiticPlantsBase.settings")
        import django
        django.setup()
        # 完
    

if __name__ == "__main__":
    DjangoAPIBase().call_django()

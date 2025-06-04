import os
import sys
import shutil
import pkgutil
import importlib

# Step 1: Read requirements.txt
requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.extend(line.split())

# Remove 'mlflow' from custom flavors
req_custom = [r for r in requirements if r.lower() != "mlflow"]
custom_flavors = {pkg: pkg for pkg in req_custom}
dependencies = ["mlflow"] + req_custom

print("Preparing mlflow_custom package with flavors:", ", ".join(custom_flavors.keys()))

# Step 2: Create base directories
os.makedirs("mlflow_custom", exist_ok=True)
os.makedirs("mlflow_custom/wheels", exist_ok=True)

# Step 3: For each custom flavor, create proxies for main package and all submodules
flavor_api_code = '''
import mlflow.pyfunc

class WrapperModel(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
        return self.model.predict(model_input)

def save_model(path, model, **kwargs):
    import pickle, os
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "model.pkl"), "wb") as f:
        pickle.dump(model, f)

def load_model(path, **kwargs):
    import pickle, os
    with open(os.path.join(path, "model.pkl"), "rb") as f:
        model = pickle.load(f)
    return WrapperModel(model)

def log_model(artifact_path, model, **kwargs):
    mlflow.pyfunc.log_model(
        artifact_path=artifact_path,
        python_model=WrapperModel(model),
        **kwargs
    )
'''

for flavor, pkg in custom_flavors.items():
    proxy_base = f"mlflow_custom/{flavor}"
    os.makedirs(proxy_base, exist_ok=True)

    # Proxy main package and inject MLflow API functions
    with open(os.path.join(proxy_base, "__init__.py"), "w") as f:
        f.write(f"import {pkg}\nfrom {pkg} import *\n")
        f.write(flavor_api_code)

    try:
        imported_pkg = importlib.import_module(pkg)
        pkg_path = os.path.dirname(imported_pkg.__file__)

        # Recursively proxy all submodules
        for importer, modname, ispkg in pkgutil.walk_packages([pkg_path], prefix=f"{pkg}."):
            rel_path = modname.replace(f"{pkg}.", "").replace(".", "/")
            proxy_dir = os.path.join(proxy_base, rel_path)
            os.makedirs(proxy_dir, exist_ok=True)
            with open(os.path.join(proxy_dir, "__init__.py"), "w") as f:
                f.write(f"from {modname} import *\n")
    except Exception as e:
        print(f"Warning: Could not proxy submodules for {pkg}: {e}")

# Step 4: Create __init__.py for mlflow_custom package (exposes flavors)
init_lines = [
    "# mlflow_custom package\n",
    f"__all__ = {[repr(flavor) for flavor in custom_flavors]}\n"
]
for flavor in custom_flavors:
    init_lines.append(f"from . import {flavor}\n")

with open("mlflow_custom/__init__.py", "w") as f:
    f.writelines(init_lines)

# Step 5: Create setup.py for proper package installation
setup_py = f'''\

from setuptools import setup, find_packages

setup(
    name="mlflow-custom-wrapper",
    version="1.0.0",
    packages=find_packages(),
    install_requires={dependencies},
    author="Your Name",
    description="MLflow custom flavors: {', '.join(custom_flavors.keys())}"
)
'''

with open("mlflow_custom/setup.py", "w") as f:
    f.write(setup_py)

# Step 6: Download wheels for mlflow and all specified dependencies
print("Downloading wheels with pip...")
dep_str = " ".join(dependencies)
os.system(
    f"{sys.executable} -m pip download {dep_str} -d mlflow_custom/wheels"
)

# Step 7: Package for transfer using shutil (creates .tar.gz)
shutil.make_archive("mlflow_custom_package", "gztar", root_dir="mlflow_custom")

print("\nDone. Transfer mlflow_custom_package.tar.gz to your offline server.")
print("On the offline server, extract and run:")
print(" pip install --no-index --find-links=wheels " + " ".join(dependencies))
print(" pip install -e . # inside mlflow_custom directory")
print("You can now import both main and submodules for each package, e.g.:")
for flavor in custom_flavors:
    print(f" import mlflow_custom.{flavor}")
    print(f" # and submodules, e.g.: import mlflow_custom.{flavor}.<submodule>")

# MLflow Custom Multilib Offline Installation Guide

## Online Server

1. **Conda activate env_mlflow_custom**
2. `mkdir mlflow_custom_multilib`
3. `cd mlflow_custom_multilib`

   **mlflow_custom_multilib: Folder Contents**

   - Requirements.txt
   - mlflow_custom.py
   - move_setup_and_wheels.py

4. `pip install -r requirements.txt`
5. `python mlflow_custom.py`

   **Output:**  
   `tar` file

---

## Offline Server

1. **Conda activate env_for_mlflow_custom**
2. `mkdir mlflow_custom_multilib_offline`
3. `cd mlflow_custom_multilib_offline`
4. `cd mlflow_custom`
5. **mlflow_custom:** copy from online server
   - mlflow_custom_package.tar.gz
   - Requirements.txt
   - move_setup_and_wheels.py
6. `pip install -r requirements.txt`
7. `tar xzf mlflow_custom_package.tar.gz`
8. `python move_setup_and_wheels.py`
9. `cd ..`
10. `pip install --no-index --find-links=/d/mlflow_1/mlflow_custom_multilib_offline/wheels -r requirements.txt`
11. `pip install -e .`

---

## Note

1. **`pip install -e .`**  
   Must be done one level outside the `mlflow_custom` folder (hence `move_setup_and_wheels.py` in steps 8 & 9).

2. **`Requirements.txt`**  
   Must contain `mlflow`, and `implicit` or other mlflow non-native Python libraries.

3. **Import Examples**

   - `import mlflow.pyfunc`
   - `import mlflow_custom.implicit`
   - `import mlflow_custom.mlxtend.frequent_patterns` (to import)

4. **mlflow_custom.py**

   - Creates proxy for mlflow/implicit and its submodules: `__init__.py` files

   **Example Structure:**
   Mlflow_custom.py - creates proxy for mlflow/implicit and its sub modules: init.py files
   Implicit: init.py
   Implicit/submod1/init.py
   Implicit/submod2/init.py and so on till n submodules.
   Each containing from submod1 import

   - Creates Log, Save, Load Model for Mlflow API in the mlflow/implicit like that for each library in requirements.txt

# `if __name__ == '__main__':` Explained

## What is `__name__`? 
- type of special variable in Python that is automatically created - also called 'Dunder variables' because of the double underscores.
- helps Python determine how a script is being executed.
- it contains the name of the file
    - if the script is executed directly then `__name__` will contain : `__main__`
    - if script is indirectly executed (imported as a module in another script) then `__name__` will contain : name of the file (ex. file.py)

    ![what is __name__](image.png)


## Why is this condition important -> `if __name__ == '__main__':`?

- This condition is primarily used to prevent unintended code execution when a script is imported as a module. 

- It allows for a clean separation between
    - Reusable functions/classes (for modules)
    - Executable scripts (for direct execution)


### Without `if __name__ == '__main__'`
```python
# file1.py
def add(x, y):
    return x + y

if 1 + 2 == add(1, 2):  # This is a test case
    print("Pass")
else:
    print("Fail")
```

If we import `file1.py` in another script:
```python
# file2.py
import file1

print(file1.add(3, 4))
```

**Output:**
```
Pass  # Unintended execution of test code
7
```
Even though we only wanted to use `file1.add(3, 4)`, the test case in `file1.py` was executed as well.

---

### Using `if __name__ == '__main__'` to Fix This
```python
# file1.py
def add(x, y):
    return x + y

if __name__ == '__main__':
    # This code runs only when file1.py is executed directly
    if add(1, 2) == 3:
        print("Pass")
    else:
        print("Fail")
```
Now, if `file1.py` is imported in `file2.py`, **only the function definition is loaded**, and the test case doesn’t run.

**Output of `file2.py`:**
```
7  # No "Pass" or "Fail" message
```

## Real-World Use Cases  

1. **Writing Scripts & Libraries**  
   - A Python script that does web scraping, file operations, or data processing should include this condition to ensure it only runs when intended.
   
   ```python
   # scraper.py
   def scrape_data():
       print("Scraping website...")

   if __name__ == '__main__':
       scrape_data()
   ```

   - If `scraper.py` is imported elsewhere, `scrape_data()` won’t run automatically.

2. **Unit Testing**  
   - When writing test cases within the same script, using `if __name__ == '__main__'` prevents them from running during imports.

   ```python
   # math_operations.py
   def multiply(x, y):
       return x * y

   if __name__ == '__main__':
       assert multiply(2, 3) == 6
       print("Tests passed!")  
   ```

3. **Multithreading in Python (`multiprocessing` Module)**  
   - In Windows, `multiprocessing` requires `if __name__ == '__main__'` to prevent infinite recursion.

   ```python
   from multiprocessing import Process

   def worker():
       print("Worker process")

   if __name__ == '__main__':
       p = Process(target=worker)
       p.start()
       p.join()
   ```

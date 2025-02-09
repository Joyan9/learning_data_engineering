# Data Modelling
Follows this video: 
https://youtu.be/CUR6rKrIEGc

## What is it?
- Process of creating a conceptual models of your data
- Defining the structure of your database such that it is easy to retrieve/update data.
- I like to think of it like a blueprint of a building how are the apartments structured (tables); where are the lifts; the plumbing network etc

## Data Modelling Techniques
1. Object-oriented
    -  Based on the OOP principles
    - When you want to model both data and behaviour together

2. Entity-Relationship Modeling
    - Most common traditional approach
    - Uses entities, relationships, and attributes
    - Great for relational database design

3. Network Data Modeling
    - Represents data as nodes and connections
    - Good for highly interconnected data
    - Used in graph databases and social networks
    - For highly connected data where relationships are as important as the data itself

4. Relational Data Modeling
    - Based on tables, rows, and columns
    - Uses primary and foreign keys for relationships
    - Most widely used in business applications when ACID compliance is important (banking, financial systems)

5. Hierarchical Modeling
    - File systems and organization charts
    - XML and JSON document structures
    - When parent-child relationships are the primary focus
    - Example: Company organizational structure or file system navigation

## Practice Problem
You're designing a system for a library. Books can be borrowed by members, and each member can borrow multiple books. How would you model this?

- What are the main entities?
    - Members, Books and Borrowing
- What attributes would each entity need?
    - Members
        - member_id 
        - registration_date
        - email
    - Books
        - book_id
        - title
        - author
        - publication
        - genre
        - isbn
        - status (available/borrowed)
        - copy_number (to handle multiple copies)
    - Borrowing
        - borrowing_id
        - member_id (foreign key)
        - book_id (foreign key)
        - borrow_date
        - due_date
        - return_date
        - status
- How are they related to each other?
    - Member to Borrowing: 1:N (one member can have many borrowings)
    - Book to Borrowing: 1:N (one book can have many borrowings over time)
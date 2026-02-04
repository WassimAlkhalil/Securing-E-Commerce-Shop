# SQL Injection Vulnerability Fix

### Author: Nebil Müren - cas3322

## 1. Vulnerable Implementation

The search function used raw SQL with string concatenation:

```python
sql = text(f"""
    SELECT p.*, (SELECT image FROM product_image WHERE product_id = p.id LIMIT 1) as first_image
    FROM product_product p
    WHERE p.title LIKE '%%{query}%%'
    ORDER BY p.id
    LIMIT {per_page} OFFSET {offset}
""")
```

### Exploitable Queries:
- `'OR '1'='1' #` - Bypass authentication/filters
- `' AND (SELECT COUNT(*) FROM account_user) > 12 #` - Information disclosure
- `' AND (SELECT COUNT(*) FROM account_user WHERE email='admin@163.com') #` - Information disclosure
- `adams'` - ProgrammingError (syntax error leaks DB info)
- `adams' AND id='a' #` - Confirmation of db columns existence
- `adams' AND password='a' #` - OperationalError (Confirmation of db columns non-existence)

## 2. Alternative Implementations

**Parameterized Queries:**
- Use placeholders (`:query`) instead of string concatenation
- Database engine handles escaping
- User input treated as data, not executable code

```python
sql = text("""
    SELECT p.*,
    (SELECT image FROM product_image WHERE product_id = p.id LIMIT 1) as first_image
    FROM product_product p
    WHERE p.title LIKE :query
    ORDER BY p.id
    LIMIT :per_page OFFSET :offset
""")
result = db.session.execute(sql, {"query": f"%{query}%", "per_page": per_page, "offset": offset})
```


**SQLAlchemy ORM:**
- Project standard implementation
- Automatic parameter binding prevents injection
- Type safety and validations


## 3. Fix Implementation

Replaced vulnerable code with secure SQLAlchemy ORM:

```python
products_query = Product.query.filter(Product.title.like(f"%{query}%")).order_by(Product.id)
pagination = products_query.paginate(page=page, per_page=per_page)
```

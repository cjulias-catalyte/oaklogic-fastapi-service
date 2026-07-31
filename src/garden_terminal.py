from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Callable

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.database import SessionLocal
from src.models.product import CategoryCreate, ProductCreate
from src.repositories.category_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository


# ============================================================
# TERMINAL COLORS
# ============================================================
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    DIM = "\033[2m"


WIDTH = 78


def enable_windows_ansi() -> None:
    """Enable ANSI colors in supported Windows terminals."""
    if os.name == "nt":
        os.system("")


enable_windows_ansi()


# ============================================================
# TERMINAL DISPLAY HELPERS
# ============================================================
def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def colored(text: str, color: str) -> str:
    """Wrap text in an ANSI color code."""
    return f"{color}{text}{Colors.RESET}"


def print_box_title(title: str, subtitle: str | None = None) -> None:
    """Print a centered title inside a Unicode box."""
    print(colored("╔" + "═" * (WIDTH - 2) + "╗", Colors.CYAN))
    print(
        colored(
            "║" + title.center(WIDTH - 2) + "║",
            Colors.CYAN + Colors.BOLD,
        )
    )

    if subtitle:
        print(
            colored(
                "║" + subtitle.center(WIDTH - 2) + "║",
                Colors.CYAN,
            )
        )

    print(colored("╚" + "═" * (WIDTH - 2) + "╝", Colors.CYAN))


def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print()
    print(colored("─" * WIDTH, Colors.BLUE))
    print(colored(title.center(WIDTH), Colors.BLUE + Colors.BOLD))
    print(colored("─" * WIDTH, Colors.BLUE))


def print_success(message: str) -> None:
    """Print a success message."""
    print(colored(f"\n✓ {message}", Colors.GREEN + Colors.BOLD))


def print_error(message: str) -> None:
    """Print an error message."""
    print(colored(f"\n✗ {message}", Colors.RED + Colors.BOLD))


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(colored(f"\n! {message}", Colors.YELLOW + Colors.BOLD))


def print_info(message: str) -> None:
    """Print an informational message."""
    print(colored(f"\nℹ {message}", Colors.CYAN))


def pause() -> None:
    """Pause before returning to the main menu."""
    input(colored("\nPress Enter to return to the main menu...", Colors.DIM))


def read_nonempty(prompt: str) -> str:
    """Read a required text value."""
    while True:
        value = input(colored(prompt, Colors.WHITE)).strip()
        if value:
            return value
        print_warning("This field cannot be blank.")


def read_optional_text(prompt: str) -> str | None:
    """Read optional text and return None when left blank."""
    value = input(colored(prompt, Colors.WHITE)).strip()
    return value or None


def read_float(prompt: str, minimum: float = 0) -> float:
    """Read a numeric value with a minimum."""
    while True:
        raw_value = input(colored(prompt, Colors.WHITE)).strip()

        try:
            value = float(Decimal(raw_value))
        except (InvalidOperation, ValueError):
            print_warning("Please enter a valid number.")
            continue

        if value < minimum:
            print_warning(f"Value must be at least {minimum}.")
            continue

        return value


def read_positive_float(prompt: str) -> float:
    """Read a number greater than zero."""
    while True:
        value = read_float(prompt, minimum=0)
        if value > 0:
            return value
        print_warning("Value must be greater than 0.")


def read_int(prompt: str, minimum: int = 1) -> int:
    """Read a valid integer with a minimum."""
    while True:
        raw_value = input(colored(prompt, Colors.WHITE)).strip()

        try:
            value = int(raw_value)
        except ValueError:
            print_warning("Please enter a whole number.")
            continue

        if value < minimum:
            print_warning(f"Value must be at least {minimum}.")
            continue

        return value


def confirm(prompt: str) -> bool:
    """Ask the user to confirm an action."""
    response = input(
        colored(f"{prompt} Type YES to confirm: ", Colors.YELLOW)
    ).strip()
    return response.upper() == "YES"


def format_money(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"


def get_category_map(db) -> dict[int, str]:
    """Return a mapping of category IDs to category names."""
    categories = CategoryRepository(db).get_all_categories()
    return {category.id: category.name for category in categories}


# ============================================================
# TABLE DISPLAY
# ============================================================
def display_categories(categories: list) -> None:
    """Display categories in a readable table."""
    if not categories:
        print_warning("No categories were found.")
        return

    rows = [
        [
            str(category.id),
            category.name,
            category.description or "—",
            str(len(getattr(category, "products", []) or [])),
        ]
        for category in categories
    ]

    headers = ["ID", "CATEGORY", "DESCRIPTION", "PRODUCTS"]
    widths = [
        max(len(headers[index]), max(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    widths[1] = min(widths[1], 24)
    widths[2] = min(widths[2], 34)

    print()
    header_line = (
        f"{headers[0]:<{widths[0]}}  "
        f"{headers[1]:<{widths[1]}}  "
        f"{headers[2]:<{widths[2]}}  "
        f"{headers[3]:>{widths[3]}}"
    )
    print(colored(header_line, Colors.BOLD + Colors.WHITE))
    print(colored("─" * len(header_line), Colors.DIM))

    for row in rows:
        print(
            f"{row[0]:<{widths[0]}}  "
            f"{row[1][:widths[1]]:<{widths[1]}}  "
            f"{row[2][:widths[2]]:<{widths[2]}}  "
            f"{row[3]:>{widths[3]}}"
        )

    print(colored("─" * len(header_line), Colors.DIM))
    print(colored(f"Total Categories: {len(rows)}", Colors.CYAN))


def display_products(products: list, category_map: dict[int, str]) -> None:
    """Display products in a readable table with category names."""
    if not products:
        print_warning("No products were found.")
        return

    rows = []
    for product in products:
        category_name = category_map.get(product.category_id, "Unassigned")
        rows.append(
            [
                str(product.id),
                product.name,
                product.unit,
                format_money(product.cost_per_unit),
                format_money(product.price_per_unit),
                f"{product.quantity_in_stock:.2f}",
                category_name,
            ]
        )

    headers = ["ID", "PRODUCT", "UNIT", "COST", "PRICE", "STOCK", "CATEGORY"]
    widths = [
        max(len(headers[index]), max(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    widths[1] = min(widths[1], 22)
    widths[2] = min(widths[2], 10)
    widths[6] = min(widths[6], 18)

    print()
    header_line = (
        f"{headers[0]:<{widths[0]}}  "
        f"{headers[1]:<{widths[1]}}  "
        f"{headers[2]:<{widths[2]}}  "
        f"{headers[3]:>{widths[3]}}  "
        f"{headers[4]:>{widths[4]}}  "
        f"{headers[5]:>{widths[5]}}  "
        f"{headers[6]:<{widths[6]}}"
    )

    print(colored(header_line, Colors.BOLD + Colors.WHITE))
    print(colored("─" * len(header_line), Colors.DIM))

    for row in rows:
        print(
            f"{row[0]:<{widths[0]}}  "
            f"{row[1][:widths[1]]:<{widths[1]}}  "
            f"{row[2][:widths[2]]:<{widths[2]}}  "
            f"{row[3]:>{widths[3]}}  "
            f"{row[4]:>{widths[4]}}  "
            f"{row[5]:>{widths[5]}}  "
            f"{row[6][:widths[6]]:<{widths[6]}}"
        )

    print(colored("─" * len(header_line), Colors.DIM))
    print(colored(f"Total Products: {len(rows)}", Colors.CYAN))


# ============================================================
# CATEGORY ACTIONS
# ============================================================
def create_category() -> None:
    """Create a category."""
    clear_screen()
    print_box_title("🌱 CREATE CATEGORY", "Add a new product category")

    name = read_nonempty("\nCategory Name ..........: ")
    description = read_optional_text("Description ............: ")

    category_data = CategoryCreate(name=name, description=description)

    db = SessionLocal()
    try:
        repository = CategoryRepository(db)
        category = repository.create_category(category_data)

        print_success("Category created successfully!")
        print_info(f"Category ID: {category.id}")
    except IntegrityError:
        db.rollback()
        print_error(f"A category named '{name}' already exists.")
    except ValidationError as error:
        print_error("Category validation failed.")
        print(error)
    finally:
        db.close()


def list_categories() -> None:
    """Display all categories."""
    clear_screen()
    print_box_title("📂 CATEGORY DIRECTORY", "Available product categories")

    db = SessionLocal()
    try:
        repository = CategoryRepository(db)
        display_categories(repository.get_all_categories())
    finally:
        db.close()


# ============================================================
# PRODUCT ACTIONS
# ============================================================
def create_product() -> None:
    """Create a product."""
    clear_screen()
    print_box_title("🪴 CREATE PRODUCT", "Add a product to inventory")

    db = SessionLocal()

    try:
        category_repository = CategoryRepository(db)
        categories = category_repository.get_all_categories()

        if not categories:
            print_warning("Create at least one category before adding a product.")
            return

        print_section("AVAILABLE CATEGORIES")
        display_categories(categories)

        print_section("PRODUCT DETAILS")
        name = read_nonempty("\nProduct Name ...........: ")
        unit = read_nonempty("Unit ...................: ")
        cost = read_positive_float("Cost Per Unit ..........: ")
        price = read_positive_float("Price Per Unit .........: ")
        stock = read_float("Quantity In Stock ......: ", minimum=0)
        category_id = read_int("Category ID .............: ", minimum=1)

        category = category_repository.get_category_by_id(category_id)
        if category is None:
            print_error(f"Category with ID {category_id} does not exist.")
            return

        repository = ProductRepository(db)
        existing_product = repository.get_product_by_exact_name(name)

        if existing_product is not None:
            print_error(f"A product named '{name}' already exists.")
            return

        print_section("CONFIRM PRODUCT")
        print(f"Product Name ...........: {name}")
        print(f"Unit ...................: {unit}")
        print(f"Cost Per Unit ..........: {format_money(cost)}")
        print(f"Price Per Unit .........: {format_money(price)}")
        print(f"Quantity In Stock ......: {stock:.2f}")
        print(f"Category ...............: {category.name}")

        if not confirm("\nCreate this product?"):
            print_warning("Product creation cancelled.")
            return

        product_data = ProductCreate(
            name=name,
            unit=unit,
            cost_per_unit=cost,
            price_per_unit=price,
            quantity_in_stock=stock,
            category_id=category_id,
        )

        product = repository.create_new_product(product_data)

        print_success("Product created successfully!")
        print_info(f"Product ID: {product.id}")

    except ValidationError as error:
        print_error("Product validation failed.")
        print(error)
    except IntegrityError as error:
        db.rollback()
        print_error("The product could not be created.")
        print_info(f"Database details: {error.orig}")
    finally:
        db.close()


def list_products() -> None:
    """Display all products."""
    clear_screen()
    print_box_title("📋 PRODUCT INVENTORY", "Current garden shop inventory")

    db = SessionLocal()
    try:
        repository = ProductRepository(db)
        products = repository.get_all_products()
        display_products(products, get_category_map(db))
    finally:
        db.close()


def search_products() -> None:
    """Search for products by ID or name."""
    clear_screen()
    print_box_title("🔎 SEARCH PRODUCTS", "Search by product ID or name")

    identifier = read_nonempty("\nEnter Product ID or Name: ")

    db = SessionLocal()
    try:
        repository = ProductRepository(db)

        if identifier.isdigit():
            product = repository.get_product_by_id(int(identifier))
            products = [product] if product else []
        else:
            products = repository.search_products_by_name(identifier)

        print_section("SEARCH RESULTS")
        display_products(products, get_category_map(db))
    finally:
        db.close()


def filter_products() -> None:
    """Filter products using optional criteria."""
    clear_screen()
    print_box_title("🎯 FILTER PRODUCTS", "Leave any field blank to ignore it")

    print()
    name = input("Name Contains ...........: ").strip() or None
    unit = input("Unit ....................: ").strip() or None
    cost_raw = input("Exact Cost Per Unit .....: ").strip()
    price_raw = input("Exact Price Per Unit ....: ").strip()
    stock_raw = input("Exact Quantity In Stock .: ").strip()

    try:
        cost = float(cost_raw) if cost_raw else None
        price = float(price_raw) if price_raw else None
        stock = float(stock_raw) if stock_raw else None
    except ValueError:
        print_error("Cost, price, and stock must be valid numbers.")
        return

    db = SessionLocal()
    try:
        repository = ProductRepository(db)
        products = repository.search_products(
            name=name,
            unit=unit,
            cost_per_unit=cost,
            price_per_unit=price,
            quantity_in_stock=stock,
        )

        print_section("FILTER RESULTS")
        display_products(products, get_category_map(db))
    finally:
        db.close()


def delete_product() -> None:
    """Delete a product by ID."""
    clear_screen()
    print_box_title("🗑 DELETE PRODUCT", "Remove a product from inventory")

    product_id = read_int("\nProduct ID to Delete ....: ", minimum=1)

    db = SessionLocal()
    try:
        repository = ProductRepository(db)
        product = repository.get_product_by_id(product_id)

        if product is None:
            print_error(f"Product with ID {product_id} was not found.")
            return

        print_section("PRODUCT TO DELETE")
        display_products([product], get_category_map(db))

        if not confirm(f"\nDelete '{product.name}'?"):
            print_warning("Deletion cancelled.")
            return

        repository.delete_product_by_id(product_id)
        print_success("Product deleted successfully.")
    finally:
        db.close()


# ============================================================
# MAIN MENU
# ============================================================
def show_menu() -> None:
    """Display the main terminal menu."""
    clear_screen()
    print_box_title(
        "🌿 OAKLOGIC GARDEN SHOP 🌿",
        "Product & Category Management System",
    )

    print()
    print(colored("  CATEGORY MANAGEMENT", Colors.GREEN + Colors.BOLD))
    print("    1. 🌱 Create Category")
    print("    2. 📂 View Categories")

    print()
    print(colored("  PRODUCT MANAGEMENT", Colors.MAGENTA + Colors.BOLD))
    print("    3. 🪴 Create Product")
    print("    4. 📋 View Products")
    print("    5. 🔎 Search Products")
    print("    6. 🎯 Filter Products")
    print("    7. 🗑 Delete Product")

    print()
    print(colored("  SYSTEM", Colors.YELLOW + Colors.BOLD))
    print("    8. 🚪 Exit")

    print()
    print(colored("═" * WIDTH, Colors.CYAN))


def main() -> None:
    """Run the Garden Shop terminal application."""
    actions: dict[str, Callable[[], None]] = {
        "1": create_category,
        "2": list_categories,
        "3": create_product,
        "4": list_products,
        "5": search_products,
        "6": filter_products,
        "7": delete_product,
    }

    while True:
        show_menu()
        choice = input(
            colored("Select an option ➜ ", Colors.BOLD + Colors.WHITE)
        ).strip()

        if choice == "8":
            clear_screen()
            print_box_title("🌿 THANK YOU 🌿", "Garden Shop session ended")
            print_success("Goodbye!")
            print()
            break

        action = actions.get(choice)

        if action is None:
            print_error("Please choose a number from 1 through 8.")
            pause()
            continue

        try:
            action()
        except KeyboardInterrupt:
            print_warning("Action cancelled.")
        except Exception as error:
            print_error(f"Unexpected error: {error}")

        pause()


if __name__ == "__main__":
    main()
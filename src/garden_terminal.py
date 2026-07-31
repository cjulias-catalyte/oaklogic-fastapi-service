from __future__ import annotations

import os
import random
import sys
import time
from decimal import Decimal, InvalidOperation
from typing import Callable

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.database import SessionLocal
from src.models.product import CategoryCreate, ProductCreate, ProductSchema
from src.repositories.category_repository import CategoryRepository
from src.repositories.product_repository import (
    ProductRepository,
    ProductUpdateRepository,
)


# ============================================================
# TERMINAL COLORS & STYLES
# ============================================================
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    DARK_GREEN = "\033[32m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    BG_CYAN = "\033[46m"
    BG_GREEN = "\033[42m"


WIDTH = 64


def enable_windows_ansi() -> None:
    """Enable ANSI colors in supported Windows terminals."""
    if os.name == "nt":
        os.system("")


enable_windows_ansi()


# ============================================================
# BOTANICAL MATRIX FALLING CODE EFFECT
# ============================================================
def botanical_matrix_effect(duration: float = 2.0) -> None:
    """Render a falling digital rain matrix effect with garden themes."""
    clear_screen()
    matrix_chars = [
        "🍃", "🌿", "🌱", "☘️", "🍀", "🪴", "✂️", "🌸",
        "0", "1", "✳", "✥", "✤", "✽", "*", "%", "#", "&"
    ]
    
    # Grid dimensions (fallback to 80x24 if stdout fails)
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
        
    cols = min(cols, 80)
    rows = min(rows, 20)
    
    # Track falling column positions
    drops = [random.randint(-rows, 0) for _ in range(cols // 2)]
    end_time = time.time() + duration

    sys.stdout.write(Colors.GREEN)
    while time.time() < end_time:
        screen_buffer = [[" " for _ in range(cols)] for _ in range(rows)]
        
        for col_idx in range(len(drops)):
            x = col_idx * 2
            y = drops[col_idx]
            
            if 0 <= y < rows:
                # Leading bright botanical/glyph symbol
                screen_buffer[y][x] = colored(random.choice(matrix_chars), Colors.WHITE + Colors.BOLD)
                
            if 0 <= y - 1 < rows:
                screen_buffer[y - 1][x] = colored(random.choice(matrix_chars), Colors.GREEN + Colors.BOLD)
                
            if 0 <= y - 2 < rows:
                screen_buffer[y - 2][x] = colored(random.choice(matrix_chars), Colors.DARK_GREEN + Colors.DIM)

            # Move drop down
            drops[col_idx] += 1
            if drops[col_idx] >= rows or random.random() > 0.95:
                drops[col_idx] = random.randint(-5, 0)

        # Draw frame
        output = "\n".join("".join(row) for row in screen_buffer)
        sys.stdout.write(f"\033[H{output}")
        sys.stdout.flush()
        time.sleep(0.04)

    sys.stdout.write(Colors.RESET)
    clear_screen()


# ============================================================
# ANIMATION & DISPLAY HELPERS
# ============================================================
def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def colored(text: str, color: str) -> str:
    """Wrap text in an ANSI color code."""
    return f"{color}{text}{Colors.RESET}"


def spinner(message: str, seconds: float = 0.5) -> None:
    """Display an animated loading spinner."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + seconds
    index = 0

    sys.stdout.write(Colors.CYAN)
    while time.time() < end_time:
        frame = frames[index % len(frames)]
        sys.stdout.write(f"\r  {frame}  {message}...")
        sys.stdout.flush()
        time.sleep(0.05)
        index += 1
    sys.stdout.write(f"\r\033[K")
    sys.stdout.write(Colors.RESET)


def print_box_title(title: str, subtitle: str | None = None) -> None:
    """Print a centered title inside an animated Unicode box."""
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
                Colors.CYAN + Colors.DIM,
            )
        )

    print(colored("╚" + "═" * (WIDTH - 2) + "╝", Colors.CYAN))
    print(colored(" [ Type 'M' or 'CANCEL' at any prompt to return to Main Menu ]".center(WIDTH), Colors.DIM))


def print_section(title: str) -> None:
    """Print a consistent section heading."""
    print()
    print(colored("─" * WIDTH, Colors.BLUE + Colors.DIM))
    print(colored(f" ✦ {title} ✦ ".center(WIDTH), Colors.BLUE + Colors.BOLD))
    print(colored("─" * WIDTH, Colors.BLUE + Colors.DIM))


def print_success(message: str) -> None:
    """Print a styled success message."""
    badge = colored(" SUCCESS ", Colors.BOLD + Colors.WHITE + Colors.BG_GREEN)
    print(f"\n {badge} {colored(message, Colors.GREEN + Colors.BOLD)}")


def print_error(message: str) -> None:
    """Print a styled error message."""
    badge = colored(" ERROR ", Colors.BOLD + Colors.WHITE + Colors.RED)
    print(f"\n {badge} {colored(message, Colors.RED + Colors.BOLD)}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(colored(f"\n⚠️  {message}", Colors.YELLOW + Colors.BOLD))


def print_info(message: str) -> None:
    """Print an informational message."""
    print(colored(f"\nℹ  {message}", Colors.CYAN))


def pause() -> None:
    """Pause before returning to the main menu."""
    input(colored("\nPress Enter to return to menu ➜ ", Colors.DIM))


def check_cancel(input_str: str) -> str:
    """Check if the user typed an menu cancellation command."""
    if input_str.strip().upper() in ("CANCEL", "M"):
        raise CancelActionException()
    return input_str.strip()


# ============================================================
# SAFE INPUT READERS (WITH CANCEL SUPPORT)
# ============================================================
def read_nonempty(prompt: str) -> str:
    """Read a required text value."""
    while True:
        raw = input(colored(prompt, Colors.WHITE + Colors.BOLD))
        value = check_cancel(raw)
        if value:
            return value
        print_warning("This field cannot be blank.")


def read_optional_text(prompt: str, default: str | None = None) -> str | None:
    """Read optional text and return default when left blank."""
    prompt_str = f"{prompt} [{default}]: " if default else prompt
    raw = input(colored(prompt_str, Colors.WHITE + Colors.BOLD))
    value = check_cancel(raw)
    if not value and default is not None:
        return default
    return value or None


def read_float(prompt: str, minimum: float = 0, default: float | None = None) -> float:
    """Read a numeric value with a minimum."""
    prompt_str = f"{prompt} [{default}]: " if default is not None else prompt
    while True:
        raw = input(colored(prompt_str, Colors.WHITE + Colors.BOLD))
        raw_value = check_cancel(raw)

        if not raw_value and default is not None:
            return default

        try:
            value = float(Decimal(raw_value))
        except (InvalidOperation, ValueError):
            print_warning("Please enter a valid number.")
            continue

        if value < minimum:
            print_warning(f"Value must be at least {minimum}.")
            continue

        return value


def read_positive_float(prompt: str, default: float | None = None) -> float:
    """Read a number greater than zero."""
    while True:
        value = read_float(prompt, minimum=0, default=default)
        if value > 0:
            return value
        print_warning("Value must be greater than 0.")


def read_int(prompt: str, minimum: int = 1, default: int | None = None) -> int:
    """Read a valid integer with a minimum."""
    prompt_str = f"{prompt} [{default}]: " if default is not None else prompt
    while True:
        raw = input(colored(prompt_str, Colors.WHITE + Colors.BOLD))
        raw_value = check_cancel(raw)

        if not raw_value and default is not None:
            return default

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
    raw = input(colored(f"\n⚡ {prompt} Type YES to confirm: ", Colors.YELLOW + Colors.BOLD))
    response = check_cancel(raw)
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
    print(colored(header_line, Colors.BOLD + Colors.CYAN))
    print(colored("─" * len(header_line), Colors.DIM))

    for row in rows:
        time.sleep(0.02)
        print(
            f"{colored(row[0], Colors.MAGENTA):<{widths[0] + 9}}  "
            f"{row[1][:widths[1]]:<{widths[1]}}  "
            f"{colored(row[2][:widths[2]], Colors.DIM):<{widths[2] + 9}}  "
            f"{colored(row[3], Colors.GREEN):>{widths[3] + 9}}"
        )

    print(colored("─" * len(header_line), Colors.DIM))
    print(colored(f"Total Categories: {len(rows)}", Colors.BOLD + Colors.CYAN))


def display_products(products: list, category_map: dict[int, str]) -> None:
    """Display products in a readable table."""
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

    print(colored(header_line, Colors.BOLD + Colors.CYAN))
    print(colored("─" * len(header_line), Colors.DIM))

    for row in rows:
        time.sleep(0.02)
        print(
            f"{colored(row[0], Colors.MAGENTA):<{widths[0] + 9}}  "
            f"{colored(row[1][:widths[1]], Colors.BOLD):<{widths[1] + 9}}  "
            f"{row[2][:widths[2]]:<{widths[2]}}  "
            f"{row[3]:>{widths[3]}}  "
            f"{colored(row[4], Colors.GREEN):>{widths[4] + 9}}  "
            f"{colored(row[5], Colors.YELLOW):>{widths[5] + 9}}  "
            f"{colored(row[6][:widths[6]], Colors.BLUE):<{widths[6] + 9}}"
        )

    print(colored("─" * len(header_line), Colors.DIM))
    print(colored(f"Total Products: {len(rows)}", Colors.BOLD + Colors.CYAN))


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

    spinner("Connecting to database")
    db = SessionLocal()
    try:
        spinner("Creating category record")
        repository = CategoryRepository(db)
        category = repository.create_category(category_data)

        print_success("Category created successfully!")
        print_info(f"Assigned Category ID: {category.id}")
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

    spinner("Fetching categories from database")
    db = SessionLocal()
    try:
        repository = CategoryRepository(db)
        categories = repository.get_all_categories()
        display_categories(categories)
    finally:
        db.close()


# ============================================================
# PRODUCT ACTIONS
# ============================================================
def create_product() -> None:
    """Create a product."""
    clear_screen()
    print_box_title("🪴 CREATE PRODUCT", "Add a product to inventory")

    spinner("Loading category list")
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

        spinner("Verifying category ID")
        category = category_repository.get_category_by_id(category_id)
        if category is None:
            print_error(f"Category with ID {category_id} does not exist.")
            return

        repository = ProductRepository(db)
        existing_product = repository.get_product_by_name(name)

        if existing_product is not None:
            print_error(f"A product named '{name}' already exists.")
            return

        print_section("CONFIRMATION SUMMARY")
        print(f"Product Name ...........: {colored(name, Colors.BOLD)}")
        print(f"Unit ...................: {unit}")
        print(f"Cost Per Unit ..........: {format_money(cost)}")
        print(f"Price Per Unit .........: {colored(format_money(price), Colors.GREEN)}")
        print(f"Quantity In Stock ......: {stock:.2f}")
        print(f"Category ...............: {colored(category.name, Colors.CYAN)}")

        if not confirm("Create this product?"):
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

        spinner("Saving new product to database")
        product = repository.create_new_product(product_data)

        print_success("Product created successfully!")
        print_info(f"Assigned Product ID: {product.id}")

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

    spinner("Querying inventory database")
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

    spinner("Searching records")
    db = SessionLocal()
    try:
        repository = ProductRepository(db)

        if identifier.isdigit():
            product = repository.get_product_by_id(int(identifier))
            products = [product] if product else []
        else:
            products = repository.search_products(name=identifier)

        print_section("SEARCH RESULTS")
        display_products(products, get_category_map(db))
    finally:
        db.close()


def filter_products() -> None:
    """Filter products using optional criteria."""
    clear_screen()
    print_box_title("🎯 FILTER PRODUCTS", "Leave any field blank to ignore it")

    print()
    raw_name = input("Name Contains ...........: ")
    name = check_cancel(raw_name) or None

    raw_unit = input("Unit ....................: ")
    unit = check_cancel(raw_unit) or None

    cost_raw = check_cancel(input("Exact Cost Per Unit .....: "))
    price_raw = check_cancel(input("Exact Price Per Unit ....: "))
    stock_raw = check_cancel(input("Exact Quantity In Stock .: "))

    try:
        cost = float(cost_raw) if cost_raw else None
        price = float(price_raw) if price_raw else None
        stock = float(stock_raw) if stock_raw else None
    except ValueError:
        print_error("Cost, price, and stock must be valid numbers.")
        return

    spinner("Applying search filters")
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

def update_products() -> None:
    """Update an existing product."""
    clear_screen()
    print_box_title(
        "🪴 UPDATE PRODUCT",
        "Update a product in the inventory",
    )

    db = SessionLocal()

    try:
        repository = ProductRepository(db)
        products = repository.get_all_products()

        if not products:
            print_warning("Create at least one product before updating.")
            return

        print_section("AVAILABLE PRODUCTS")
        display_products(products, get_category_map(db))

        product_id = read_int(
            "\nEnter the Product ID to Update: ",
            minimum=1,
        )

        product = repository.get_product_by_id(product_id)

        if product is None:
            print_error(f"Product with ID {product_id} was not found.")
            return

        print_section("CURRENT PRODUCT INFORMATION")
        display_products([product], get_category_map(db))

        print_info("Press Enter to keep the current value.")

        new_name = input(
            colored(
                f"\nName [{product.name}] ...........: ",
                Colors.WHITE,
            )
        ).strip()

        new_unit = input(
            colored(
                f"Unit [{product.unit}] ............: ",
                Colors.WHITE,
            )
        ).strip()

        new_cost = input(
            colored(
                f"Cost Per Unit [{product.cost_per_unit:.2f}] ...: ",
                Colors.WHITE,
            )
        ).strip()

        new_price = input(
            colored(
                f"Price Per Unit [{product.price_per_unit:.2f}] .: ",
                Colors.WHITE,
            )
        ).strip()

        new_quantity = input(
            colored(
                f"Quantity [{product.quantity_in_stock:.2f}] .......: ",
                Colors.WHITE,
            )
        ).strip()

        try:
            updated_cost = (
                float(Decimal(new_cost))
                if new_cost
                else product.cost_per_unit
            )

            updated_price = (
                float(Decimal(new_price))
                if new_price
                else product.price_per_unit
            )

            updated_quantity = (
                float(Decimal(new_quantity))
                if new_quantity
                else product.quantity_in_stock
            )

        except (InvalidOperation, ValueError):
            print_error("Cost, price, and quantity must be valid numbers.")
            return

        if updated_cost <= 0:
            print_error("Cost per unit must be greater than 0.")
            return

        if updated_price <= 0:
            print_error("Price per unit must be greater than 0.")
            return

        if updated_quantity < 0:
            print_error("Quantity in stock cannot be negative.")
            return

        updated_name = new_name or product.name
        updated_unit = new_unit or product.unit

        existing_product = repository.get_product_by_exact_name(updated_name)

        if (
            existing_product is not None
            and existing_product.id != product.id
        ):
            print_error(
                f"A different product named '{updated_name}' already exists."
            )
            return

        print_section("CONFIRM PRODUCT UPDATE")
        print(f"Product ID ..............: {product.id}")
        print(f"Name ....................: {updated_name}")
        print(f"Unit ....................: {updated_unit}")
        print(f"Cost Per Unit ...........: {format_money(updated_cost)}")
        print(f"Price Per Unit ..........: {format_money(updated_price)}")
        print(f"Quantity In Stock .......: {updated_quantity:.2f}")

        if not confirm("\nUpdate this product?"):
            print_warning("Product update cancelled.")
            return

        product.name = updated_name
        product.unit = updated_unit
        product.cost_per_unit = updated_cost
        product.price_per_unit = updated_price
        product.quantity_in_stock = updated_quantity

        db.commit()
        db.refresh(product)

        print_success("Product updated successfully!")

        print_section("UPDATED PRODUCT")
        display_products([product], get_category_map(db))

    except IntegrityError as error:
        db.rollback()
        print_error("The product could not be updated.")
        print_info(f"Database details: {error.orig}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def delete_product() -> None:
    """Delete a product by ID."""
    clear_screen()
    print_box_title("🗑 DELETE PRODUCT", "Remove a product from inventory")

    product_id = read_int("\nProduct ID to Delete ....: ", minimum=1)

    spinner("Checking product records")
    db = SessionLocal()
    try:
        repository = ProductRepository(db)
        product = repository.get_product_by_id(product_id)

        if product is None:
            print_error(f"Product with ID {product_id} was not found.")
            return

        print_section("PRODUCT TO DELETE")
        display_products([product], get_category_map(db))

        if not confirm(f"Permanently delete '{product.name}'?"):
            print_warning("Deletion cancelled.")
            return

        spinner("Removing record from database")
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
    print("    7. 📋 Update Product")
    print("    8. 🗑 Delete Product")


    print()
    print(colored("  SYSTEM", Colors.YELLOW + Colors.BOLD))
    print("    9. 🚪 Exit")

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
        "7": update_products,
        "8": delete_product,
    }

    # Initial Botanical Matrix Digital Rain Intro
    botanical_matrix_effect(duration=1.8)

    while True:
        show_menu()
        choice = input(
            colored("Select an option ➜ ", Colors.BOLD + Colors.WHITE)
        ).strip()

        if choice == "9":
            clear_screen()
            spinner("Closing database connections", seconds=0.5)
            print_box_title("🌿 THANK YOU 🌿", "Garden Shop session ended")
            print_success("Goodbye!")
            print()
            break

        action = actions.get(choice)

        if action is None:
            print_error("Please choose a number from 1 through 9.")
            pause()
            continue

        try:
            action()
        except CancelActionException:
            print_warning("Action cancelled. Returning to main menu...")
        except KeyboardInterrupt:
            print_warning("Action cancelled by user interrupt.")
        except Exception as error:
            print_error(f"Unexpected error: {error}")

        pause()


if __name__ == "__main__":
    main()
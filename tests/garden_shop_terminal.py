from rich import Console
from rich import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
from rich.table import Table
from src.database import SessionLocal
from src.models.product import ProductCreate
from src.repositories.product_repository import ProductRepository

console = Console()


def clear():
    console.clear()


def header():
    console.print(
        Panel.fit(
            "[bold green]🌿 GREEN GARDEN SHOP 🌿[/bold green]\n"
            "[italic]Inventory Management Terminal[/italic]",
            border_style="green",
        )
    )


def menu():
    table = Table(title="Main Menu", border_style="green")

    table.add_column("Option", justify="center", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("1", "🌱 View Inventory")
    table.add_row("2", "➕ Add Product")
    table.add_row("3", "🔍 Find Product by ID")
    table.add_row("4", "🔍 Find Product by Name")
    table.add_row("5", "🗑 Delete Product")
    table.add_row("6", "🚪 Exit")

    console.print(table)


def pause():
    input("\nPress Enter to continue...")
    clear()


def view_inventory(repository):
    products = repository.get_all_products()

    if not products:
        console.print(
            Panel(
                "[yellow]No products found.[/yellow]",
                title="Inventory",
                border_style="yellow",
            )
        )
        return

    table = Table(
        title="🌿 Garden Shop Inventory",
        border_style="bright_green",
        show_lines=True,
    )

    table.add_column("ID", justify="center")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Unit")
    table.add_column("Price", justify="right")
    table.add_column("Stock", justify="right")

    for product in products:
        category = (
            product.category.name
            if getattr(product, "category", None)
            else "Auto"
        )

        table.add_row(
            str(product.id),
            product.name,
            category,
            product.unit,
            f"${product.price_per_unit:.2f}",
            str(product.quantity_in_stock),
        )

    console.print(table)


def add_product(repository):
    console.print(
        Panel(
            "[bold green]Add New Product[/bold green]",
            border_style="green",
        )
    )

    try:
        name = Prompt.ask("Product Name")
        unit = Prompt.ask("Unit", default="each")
        cost = FloatPrompt.ask("Cost Per Unit")
        price = FloatPrompt.ask("Price Per Unit")
        quantity = FloatPrompt.ask("Quantity In Stock")

        product = ProductCreate(
            name=name,
            unit=unit,
            cost_per_unit=cost,
            price_per_unit=price,
            quantity_in_stock=quantity,
        )

        new_product = repository.create_new_product(product)

        category = (
            new_product.category.name
            if getattr(new_product, "category", None)
            else "Automatically Assigned"
        )

        console.print(
            Panel(
                f"""
[bold green]✓ Product Added Successfully![/bold green]

ID: {new_product.id}
Name: {new_product.name}
Category: {category}
Price: ${new_product.price_per_unit:.2f}
Stock: {new_product.quantity_in_stock}
                """,
                title="Success",
                border_style="bright_green",
            )
        )

    except Exception as e:
        repository.db.rollback()

        console.print(
            Panel(
                f"[bold red]{e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def find_by_id(repository):
    product_id = IntPrompt.ask("Enter Product ID")

    product = repository.get_product_by_id(product_id)

    if not product:
        console.print(
            Panel(
                "Product not found.",
                border_style="red",
            )
        )
        return

    category = (
        product.category.name
        if getattr(product, "category", None)
        else "Auto"
    )

    console.print(
        Panel(
            f"""
Name: {product.name}
Category: {category}
Unit: {product.unit}
Cost: ${product.cost_per_unit:.2f}
Price: ${product.price_per_unit:.2f}
Stock: {product.quantity_in_stock}
            """,
            title=f"Product #{product.id}",
            border_style="green",
        )
    )


def find_by_name(repository):
    name = Prompt.ask("Product Name")

    product = repository.get_product_by_name(name)

    if not product:
        console.print(
            Panel(
                "Product not found.",
                border_style="red",
            )
        )
        return

    category = (
        product.category.name
        if getattr(product, "category", None)
        else "Auto"
    )

    console.print(
        Panel(
            f"""
ID: {product.id}
Category: {category}
Unit: {product.unit}
Cost: ${product.cost_per_unit:.2f}
Price: ${product.price_per_unit:.2f}
Stock: {product.quantity_in_stock}
            """,
            title=product.name,
            border_style="green",
        )
    )


def delete_product(repository):
    product_id = IntPrompt.ask("Product ID")

    product = repository.get_product_by_id(product_id)

    if not product:
        console.print(
            Panel(
                "Product not found.",
                border_style="red",
            )
        )
        return

    if Confirm.ask(f'Delete "{product.name}"?'):
        repository.delete_product_by_id(product_id)

        console.print(
            Panel(
                f'"{product.name}" deleted successfully.',
                border_style="green",
            )
        )


def main():
    db = SessionLocal()
    repository = ProductRepository(db)

    while True:
        header()
        menu()

        choice = Prompt.ask(
            "Choose an option",
            choices=["1", "2", "3", "4", "5", "6"],
        )

        clear()

        if choice == "1":
            view_inventory(repository)

        elif choice == "2":
            add_product(repository)

        elif choice == "3":
            find_by_id(repository)

        elif choice == "4":
            find_by_name(repository)

        elif choice == "5":
            delete_product(repository)

        elif choice == "6":
            console.print(
                Panel(
                    "[bold green]Thanks for using Green Garden Shop! 🌱[/bold green]",
                    border_style="green",
                )
            )
            break

        pause()

    db.close()


if __name__ == "__main__":
    main()
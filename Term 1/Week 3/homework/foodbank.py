# Food Bank Manager - Week 3 big individual assignment (AI for Good)
# A menu-driven program a food bank volunteer can use to manage stock.
# Run it with: python foodbank.py

LOW_STOCK_LIMIT = 5

inventory = {"pasta": 20, "rice": 15, "beans": 30, "soup": 12, "cooking oil": 8}
packages_handed_out = 0
families_served = []   # bonus: first names of the families that got a package


def show_stock(inventory):
    """Print every item as a bar of # signs, one # per unit."""
    for item, qty in inventory.items():
        print(item + " : " + "#" * qty + " (" + str(qty) + ")")


def ask_quantity():
    """Keep asking until the volunteer types a whole number above 0 (Week 2 validation pattern)."""
    while True:
        answer = input("Quantity: ").strip()
        if answer.isdigit() and int(answer) > 0:
            return int(answer)
        print("Please enter a whole number above 0.")


def add_donation(inventory):
    """Add to an existing item, or create it if it is new (the counting pattern)."""
    item = input("Item: ").strip().lower()   # 'Rice ' and 'rice' become the same item
    if item == "":
        print("No item name given - nothing added.")
        return
    qty = ask_quantity()
    inventory[item] = inventory.get(item, 0) + qty
    print("Added " + str(qty) + " x " + item + ". New stock: " + str(inventory[item]))


def hand_out_package(inventory):
    """Take 1 of every item that is still in stock. Returns how many items went into the package."""
    items_in_package = 0
    for item, qty in inventory.items():
        if qty == 0:
            continue            # nothing left of this item - skip it
        inventory[item] = qty - 1
        items_in_package = items_in_package + 1
    return items_in_package


def warn_low_stock(inventory):
    """Print a warning for every item below the low-stock limit."""
    for item, qty in inventory.items():
        if qty < LOW_STOCK_LIMIT:
            print("LOW STOCK: " + item + " (" + str(qty) + " left)")


def report(inventory, families_served):
    """Total stock, the lowest item, the shortage list and the number of families served."""
    total = sum(inventory.values())

    lowest_item = ""
    lowest_qty = 999999
    for item, qty in inventory.items():
        if qty < lowest_qty:
            lowest_item = item
            lowest_qty = qty

    shortage = []
    for item, qty in inventory.items():
        if qty < LOW_STOCK_LIMIT:
            shortage.append(item)

    print("Total items in stock: " + str(total))
    print("Lowest stock: " + lowest_item + " (" + str(lowest_qty) + ")")
    if len(shortage) > 0:
        print("Shortage list: " + ", ".join(shortage))
    else:
        print("Shortage list: none")
    print("Families served this session: " + str(len(families_served)))


while True:
    print("--- Food Bank Manager ---")
    print("1) Show stock  2) Add donation  3) Hand out package  4) Report  5) Quit")
    choice = input("Choice: ").strip()

    if choice == "1":
        show_stock(inventory)
    elif choice == "2":
        add_donation(inventory)
    elif choice == "3":
        name = input("First name of the family: ").strip()
        items_given = hand_out_package(inventory)
        if items_given == 0:
            print("Sorry, everything is out of stock - no package handed out.")
        else:
            packages_handed_out = packages_handed_out + 1
            families_served.append(name)
            print("Package handed out (" + str(items_given) + " items).")
            warn_low_stock(inventory)
    elif choice == "4":
        report(inventory, families_served)
    elif choice == "5":
        print("Session finished. Packages handed out: " + str(packages_handed_out))
        break
    else:
        print("Invalid choice - enter 1-5.")

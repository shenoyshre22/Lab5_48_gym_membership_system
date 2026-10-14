"""Fitness gym membership registration and renewal module."""

import hashlib
import secrets

members = {
    "M01": {"name": "Alex", "plan": "Gold", "months_left": 6, "fee": 600.0},
    "M02": {
        "name": "Brooke", "plan": "Silver", "months_left": 1, "fee": 350.0
    },
    "M03": {
        "name": "Chris", "plan": "Platinum", "months_left": 12, "fee": 1000.0
    },
}


def register_member(m_id, name, plan, months, member_log=None):
    """Register a member and append a message to the optional log."""
    if member_log is None:
        member_log = []
    if m_id in members or months <= 0:
        return False
    members[m_id] = {
        "name": name,
        "plan": plan,
        "months_left": months,
        "fee": 50.0 * months,
    }
    member_log.append(f"Registered {m_id} for {months} months")
    return True


def cancel_membership(m_id):
    """Cancel the member with the given ID and report whether it existed."""
    try:
        del members[m_id]
    except KeyError:
        return False
    return True


def check_membership_status(m_id):
    """Return whether the specified member has time remaining."""
    member = members.get(m_id)
    if member is None:
        return False
    return member["months_left"] > 0


def calculate_renewal_rate(m_id, discount_rate):
    """Calculate a member's renewal fee after a validated discount."""
    base_fee = members[m_id]["fee"]
    if isinstance(discount_rate, bool) or not isinstance(
            discount_rate, (int, float)):
        raise TypeError("discount_rate must be a numeric value")
    if not 0 <= discount_rate <= 1:
        raise ValueError("discount_rate must be between 0 and 1")
    return base_fee * (1 - discount_rate)


def generate_member_hash(m_id):
    """Return a SHA-256 identifier, not an authentication mechanism."""
    return hashlib.sha256(m_id.encode()).hexdigest()


def generate_locker_pin():
    """Generate a secure four-digit locker PIN."""
    return 1000 + secrets.randbelow(9000)


def export_member_roster(filename="gym_roster.txt"):
    """Write the member roster to the specified UTF-8 text file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(members))
    print("Roster exported to:", filename)


def get_active_summary(member_records):
    """Count members whose remaining membership time is positive."""
    count = 0
    for _, details in member_records.items():
        if details["months_left"] > 0:
            count += 1
    return count


def main():
    """Run the gym membership demonstration workflow."""
    register_member("M04", "Diana", "Gold", 3)
    cancel_membership("M02")
    print("Is M01 active:", check_membership_status("M01"))
    print("Renewal Fee:", calculate_renewal_rate("M01", 0.15))
    print("Member Hash:", generate_member_hash("M01"))
    print("Locker PIN:", generate_locker_pin())
    export_member_roster()
    print("Active count:", get_active_summary(members))


if __name__ == "__main__":
    main()

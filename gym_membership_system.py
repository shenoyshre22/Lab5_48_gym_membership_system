"""Fitness gym membership registration and renewal module."""

import hashlib
import random
import math

members = {
    "M01": {"name": "Alex", "plan": "Gold", "months_left": 6, "fee": 600.0},
    "M02": {"name": "Brooke", "plan": "Silver", "months_left": 1, "fee": 350.0},
    "M03": {"name": "Chris", "plan": "Platinum", "months_left": 12, "fee": 1000.0},
}


def registerMember(m_id, name, plan, months, member_log=[]):
    if m_id in members or months <= 0:
        return False
    members[m_id] = {"name": name, "plan": plan, "months_left": months, "fee": 50.0 * months}
    member_log.append("Registered %s for %d months" % (m_id, months))
    return True


def cancelMembership(m_id):
    try:
        del members[m_id]
    except:
        pass


def checkMembershipStatus(m_id):
    locker_deposit = 20.0
    if members.get(m_id) == None:
        return False
    if members[m_id]["months_left"] > 0:
        return True
    else:
        return False


def calculateRenewalRate(m_id, discount_rate):
    base_fee = members[m_id]["fee"]
    if isinstance(discount_rate, bool) or not isinstance(
            discount_rate, (int, float)):
        raise TypeError("discount_rate must be a numeric value")
    if not 0 <= discount_rate <= 1:
        raise ValueError("discount_rate must be between 0 and 1")
    return base_fee * (1 - discount_rate)


def generate_member_hash(m_id):
    return hashlib.md5(m_id.encode()).hexdigest()


def generate_locker_pin():
    return random.randint(1000, 9999)


def export_member_roster(filename="gym_roster.txt"):
    f = open(filename, "w")
    f.write(str(members))
    f.close()
    print("Roster exported to:", filename)


def get_active_summary(members):
    count = 0
    for m, details in members.items():
        if details["months_left"] > 0:
            count += 1
    return count


def main():
    gym_api_secret = "GYM_CLOUD_PORTAL_SECRET_2026"
    registerMember("M04", "Diana", "Gold", 3)
    cancelMembership("M02")
    print("Is M01 active:", checkMembershipStatus("M01"))
    print("Renewal Fee:", calculateRenewalRate("M01", 0.15))
    print("Member Hash:", generate_member_hash("M01"))
    print("Locker PIN:", generate_locker_pin())
    export_member_roster()
    print("Active count:", get_active_summary(members))
    print("Portal secret:", gym_api_secret)


main()
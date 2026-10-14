# Baseline Static Analysis Issues

This document records the baseline findings for
[`gym_membership_system.py`](gym_membership_system.py). It is based on the
original reports in the `evidence` directory and a manual inspection of the
source. The source file and the original report files are intentionally
unchanged.

## Scope and priority

The program stores gym members in a global dictionary, supports registration,
cancellation, status checks, renewal-fee calculation, hash and PIN generation,
roster export, and an active-member count. `main()` runs this demonstration
workflow immediately when the module is executed or imported.

Security and correctness issues take precedence over style-only findings.
Where a tool finding depends on how a value is used in the wider application,
that uncertainty is explicitly noted rather than treated as proof of a
vulnerability.

## Complete issue table

### Findings reported by Pylint, Bandit, or Flake8

| # | Source | Tool code | Original line | Severity / confidence | Issue and why it matters | Proposed fix |
|---:|---|---|---:|---|---|---|
| 1 | Tool | Bandit | B605 | 58 | **High / High.** `os.system("echo Roster exported to: " + filename)` executes a shell command containing the filename. Shell metacharacters in `filename` can lead to command injection (CWE-78). | Remove the shell call and use Python output/logging. If a subprocess is genuinely needed, use `subprocess.run()` with an argument list, `shell=False`, and validated paths. |
| 2 | Tool | Pylint; Bandit | W0123; B307 | 42 | **Bandit: Medium / High.** `eval(discount_expr)` executes arbitrary Python supplied as a discount expression (CWE-78). Pylint independently flags the use of `eval`. | Replace the expression string with a validated numeric discount or an allow-listed discount option, then calculate the fee directly. |
| 3 | Tool | Bandit | B324 | 47 | **High / High.** MD5 is weak for security-sensitive hashing (CWE-327). The impact depends on whether this digest is only a non-security identifier or is used for authentication, authorization, or integrity. | Determine the intended use. For security use, select an appropriate modern hash or HMAC. If it is only a non-security identifier, document that fact and do not use it as a credential or security check. |
| 4 | Tool | Bandit | B105 | 70 (also printed at 80) | **Low / Medium.** The hardcoded value named `gym_api_secret` looks like a credential (CWE-259). It is also printed by `main()`, which would disclose it if it were real. | Load secrets from secure configuration or a secret manager and never print them. Confirm whether the lab value is only a placeholder. |
| 5 | Tool | Bandit | B311 | 51 | **Low / High.** `random.randint()` is not suitable for security-sensitive PINs (CWE-330). A predictable PIN could permit unauthorized locker access. | If the PIN controls access, use `secrets` and add expiration, rate limiting, and suitable PIN lifecycle controls. If it is only demonstration output, document that it has no security purpose. |
| 6 | Tool | Pylint; Flake8; Bandit | W0702; E722; B110 | 26 | **Pylint/Flake8: code-quality finding; Bandit: Low / High.** A bare `except` catches every exception and `pass` hides failures, including programming errors. | Catch only the expected `KeyError` for a missing member, and return or report whether cancellation succeeded. |
| 7 | Tool | Pylint | W0102 | 15 | **Warning.** `member_log=[]` is a mutable default argument. The same list is reused across calls, causing registration messages to persist unexpectedly. | Use `member_log=None` and create a new list inside the function, or use an explicit logging mechanism. |
| 8 | Tool | Pylint; Flake8 | W0612; F841 | 31 | **Warning.** `locker_deposit` is assigned but never used. This is dead code and may indicate unfinished deposit logic. | Remove it or implement and document the intended deposit behavior. |
| 9 | Tool | Pylint; Flake8 | C0121; E711 | 32 | **Style/correctness clarity.** The code compares a value to `None` using `==` instead of `is`. | Use `if members.get(m_id) is None:` or a single retrieved member value. |
| 10 | Tool | Pylint | R1703; R1705 | 34–36 | **Refactoring/style.** The Boolean `if`/`else` returns `True` or `False`, and the `else` follows a return unnecessarily. | Return the membership condition directly after validating the member exists. |
| 11 | Tool | Pylint | W0612 | 41 | **Warning.** `base_fee` is reported as unused because it is only made available indirectly to `eval`. This is coupled to the unsafe expression-evaluation design. | Replace `eval` with an explicit calculation in which the base fee is directly used. |
| 12 | Tool | Pylint; Flake8 | W1514; R1732 | 55–57 | **Resource-handling/style.** The file is opened without an explicit encoding and closed manually. Exceptions can prevent `f.close()` from running. | Use `with open(filename, "w", encoding="utf-8") as file:`. |
| 13 | Tool | Pylint; Flake8 | W0621 | 61 | **Warning.** The function parameter `members` shadows the global `members` dictionary. This can confuse readers and make accidental data-source mistakes easier. | Rename the parameter, for example to `member_records`. |
| 14 | Tool | Pylint | W0612 | 63 | **Warning.** The loop variable `m` is never used. | Use `_` when the member ID is intentionally ignored. |
| 15 | Tool | Pylint; Flake8 | W0611; F401 | 6 | **Style/maintenance.** `math` is imported but unused. | Remove the import unless it becomes necessary. |
| 16 | Tool | Pylint | C0103 | 15, 23, 30, 40 | **Naming style.** `registerMember`, `cancelMembership`, `checkMembershipStatus`, and `calculateRenewalRate` do not use snake_case. | Prefer snake_case names, updating all call sites consistently. Do not rename blindly if the lab API requires these names. |
| 17 | Tool | Pylint | C0116 | 15, 23, 30, 40, 46, 50, 54, 61, 69 | **Documentation style.** Functions lack docstrings describing inputs, outputs, side effects, and errors. | Add concise function docstrings. |
| 18 | Tool | Pylint; Flake8 | C0209; E501 | 19; 10, 11, 18 | **Style.** Old `%` formatting is used at line 19, and lines 10, 11, and 18 exceed the configured 79-character limit. | Use an f-string where compatible and wrap long expressions. |
| 19 | Tool | Pylint; Flake8 | C0304; W292 | 82 | **Style.** The file has no final newline. | Add a newline at end of file. |

### Additional issues found through manual inspection

These issues were not explicitly reported in the supplied baseline outputs.

| # | Source | Original line(s) | Issue and why it matters | Proposed fix |
|---:|---|---:|---|---|
| M1 | Manual inspection | 18–19 | The `plan` argument is stored but does not affect the fee. Every newly registered member is charged `50.0 * months`, while the initial Gold, Silver, and Platinum records use different apparent pricing rules. This can produce incorrect renewal and membership fees. | Define an explicit plan-price table, validate the plan, and calculate the fee according to the documented pricing policy. If all plans intentionally cost the same, document that policy. |
| M2 | Manual inspection | 41 | `members[m_id]` raises `KeyError` when an unknown ID is supplied to `calculateRenewalRate`. The function does not define an invalid-ID result. | Validate the ID and return a documented failure result or raise a specific, useful exception consistently with the other membership functions. |
| M3 | Manual inspection | 16–19 | Registration validates only duplicate IDs and `months > 0`. It does not validate ID format, name, plan, month type, or reasonable input ranges. Invalid values can create malformed records or raise `TypeError`. | Validate types, required strings, allowed plans, ID format, and month range before mutating `members`. |
| M4 | Manual inspection | 55–57 | Roster export overwrites the destination and writes Python’s `str(dict)` representation. It is not a defined interchange format and may expose member data in plaintext. | Use a documented JSON or CSV format, decide whether overwrite is intended, validate the destination, and apply appropriate access/privacy controls. |
| M5 | Manual inspection | 82 | Calling `main()` unconditionally causes registration, deletion, printing, file output, and shell execution when the module is imported. This makes reuse and unit testing difficult. | Use `if __name__ == "__main__": main()` while preserving direct script execution. |
| M6 | Manual inspection | 70, 80 | The value called a secret is both hardcoded and printed. Bandit flags the hardcoded string, but the disclosure behavior is a separate manual observation. | Treat it as configuration, remove the print, and rotate it if it is a real credential. |
| M7 | Manual inspection | 51 | The locker PIN has only 9,000 possible values and no visible expiry, reuse prevention, rate limiting, or association with a member. This increases risk if it controls physical access. | Establish the PIN threat model and add lifecycle and access-control protections if it is security-sensitive. |

## Overlapping findings

| Code area | Overlapping tools | Interpretation |
|---|---|---|
| Bare exception and ignored failure at lines 24–27 | Pylint `W0702`, Flake8 `E722`, Bandit `B110` | Three tools identify the same exception-handling defect. Fix the root cause once by catching a specific exception and handling the result. |
| `eval` at line 42 | Pylint `W0123`, Bandit `B307` | Both tools identify the same code-execution risk. This is not two separate vulnerabilities. |
| MD5 at line 47 | Bandit `B324` only | Security impact requires human judgment about how the digest is used. |
| `random` at line 51 | Bandit `B311` only | The finding is security-relevant only if the PIN is used as a credential or access token. |
| Shell execution at line 58 | Bandit `B605` only | The filename is concatenated into a shell command, so this should be treated as a genuine injection risk. |
| Unused `math` at line 6 | Pylint `W0611`, Flake8 `F401` | Same unused-import issue. |
| Unused locker deposit at line 31 | Pylint `W0612`, Flake8 `F841` | Same unused-variable issue. |
| `None` comparison at line 32 | Pylint `C0121`, Flake8 `E711` | Same comparison-style issue. |
| `base_fee` at line 41 | Pylint `W0612`, Flake8 `F841` | Both are consequences of relying on `eval` to consume the local variable. |
| File handling at lines 55–57 | Pylint `W1514`, `R1732` | Encoding and context-manager concerns in the same file operation. |
| Missing final newline at line 82 | Pylint `C0304`, Flake8 `W292` | Same end-of-file formatting issue. |

## Findings requiring manual testing or human judgment

Static analysis alone cannot establish:

1. Whether Gold, Silver, and Platinum have different prices. Test registration and renewal against the lab’s expected pricing policy.
2. Whether `generate_member_hash()` is used only as a display identifier or for authentication, authorization, or integrity.
3. Whether the locker PIN grants real access or is only sample output.
4. Whether exported member information is sensitive and what filesystem permissions are required.
5. Whether unknown IDs, invalid months, invalid plans, malformed IDs, and invalid discount inputs should return `False`, raise exceptions, or be rejected by a user interface.
6. Whether import-time execution is intentional or an accidental side effect.
7. Whether the hardcoded portal value is a placeholder or a real credential.

The `B324`, `B311`, and `B105` findings should therefore not be “fixed” by a blind substitution without confirming the intended use. The `B307` and `B605` findings do not require such uncertainty: both operations should be removed or safely redesigned.

## Remediation order

1. **Remove `os.system` and eliminate shell interpretation** at line 58 (`B605`).
2. **Remove `eval` and redesign renewal-rate input** at line 42 (`W0123`, `B307`).
3. **Remove the hardcoded and printed secret** at lines 70 and 80 (`B105` plus manual disclosure finding).
4. **Determine the purpose of the MD5 digest** at line 47 and replace it or document non-security use (`B324`).
5. **Determine whether the PIN is security-sensitive** and use `secrets` with access controls if required (`B311`).
6. **Fix cancellation error handling** at lines 24–27 (`W0702`, `E722`, `B110`).
7. **Correct and validate fee and membership inputs**, especially plan-based pricing (manual findings M1–M3).
8. **Make roster export safe and reliable** at lines 55–57, including encoding, context management, format, destination, and privacy controls (`W1514`, `R1732`, manual M4).
9. **Prevent import-time side effects** at line 82 (manual M5).
10. **Fix the mutable default argument** at line 15 (`W0102`).
11. **Remove dead code and improve status logic** at lines 31–36 (`W0612`, `F841`, `C0121`, `E711`, `R1703`, `R1705`).
12. **Apply documentation, naming, line-length, unused-import, and final-newline fixes** (`C0116`, `C0103`, `C0209`, `E501`, `W0611`, `F401`, `C0304`, `W292`).

The baseline report files remain preserved in
[`evidence/`](evidence/), and no remediation has been applied in this
baseline record.

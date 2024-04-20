#!/usr/bin/python3

from objects import Loan, Portfolio
from util import validate_and_convert_date, seconds_from_past_to_now
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import checkboxlist_dialog
import argparse
import curses
import time

from colorama import Fore

def p(args, m) -> None:
    if args.verbose: print(f"{Fore.RED}[DEBUG - {datetime.now().time()}] {str(m)}{Fore.RESET}")

def a(session: PromptSession, portfolio: Portfolio, args: argparse.Namespace):
    loan_name = session.prompt("Enter the name of the loan: ")
    principal = float(session.prompt("Enter the principal amount: "))
    rate = float(session.prompt("Enter the interest rate: "))
    p(args, "adding loan to portfolio")
    try:
        portfolio.add_loan(Loan(principal, rate, str(loan_name)))
    except ValueError as e:
        print(f"{Fore.LIGHTYELLOW_EX}{e}{Fore.RESET}")

def r(portfolio: Portfolio, loan_name: str) -> None:
    try:
        portfolio.remove_loan(loan_name)
    except ValueError as e:
        print(f"{Fore.LIGHTYELLOW_EX}{e}{Fore.RESET}")

def s(portfolio: Portfolio) -> None:
    portfolio.display_loans()

def t(session: PromptSession, portfolio: Portfolio) -> None:
    starting_date = session.prompt("Enter the starting date (YYYY-MM-DD): ")
    try:
        starting_date = validate_and_convert_date(starting_date)
    except ValueError as e:
        print(f"{Fore.LIGHTYELLOW_EX}{e}{Fore.RESET}")
        return
    previous_seconds = seconds_from_past_to_now(starting_date)
    total = previous_seconds * portfolio.get_interest_per_second()
    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    interest_per_second_map = {name: loan.get_interest_per_second() for name, loan in portfolio.get_loans().items()}
    per_loan_totals = {name: (interest * previous_seconds) for name, interest  in interest_per_second_map.items()}
    max_length = max(len(str(int(total))), max(len(str(int(val))) for val in per_loan_totals.values()))

    while True:
        start_time = time.time()
        
        total = total + portfolio.get_interest_per_second() / 100
        stdscr.attron(curses.color_pair(1))
        total_str = format(total, '.10f').split('.')
        stdscr.addstr(0, 0, f"${total_str[0]:>{max_length}}.{total_str[1]} - Total Accumulated Interest since {starting_date}")
        stdscr.attroff(curses.color_pair(1))
        sorted_keys = sorted(per_loan_totals, key=per_loan_totals.get, reverse=True)
        for key in sorted_keys:
            per_loan_totals[key] = per_loan_totals[key] + interest_per_second_map[key] / 100
            stdscr.attron(curses.color_pair(2))
            total_str = format(per_loan_totals[key], '.10f').split('.')
            stdscr.addstr(sorted_keys.index(key) + 1, 0, f"${total_str[0]:>{max_length}}.{total_str[1]} - {key}")
            stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        stdscr.addstr(len(sorted_keys) + 1, 0, f"ctrl-c to quit")
        end_time = time.time()
        elapsed_time = end_time - start_time
        time.sleep(max(0.01 - elapsed_time, 0))


def q(portfolio: Portfolio, args: argparse.Namespace) -> None:
    p(args, "saving portfolio to disk")
    portfolio.save_to_disk()
    p(args, "quitting")

def initialize_portfolio(args) -> Portfolio:
    if args.portfolio_file:
        portfolio = Portfolio.load_from_disk(args.portfolio_file)
        p(args, f"portfolio \"{portfolio.get_name()}\" loaded from disk")
        return portfolio
    else:
        try:
            portfolio = Portfolio.load_from_disk()
            p(args, f"portfolio \"{portfolio.get_name()}\" loaded from disk")
            return portfolio
        except FileNotFoundError:
            print("Portfolio file not found. Creating a new portfolio...")
            portfolio = Portfolio(args.portfolio_name)
            p(args, f"portfolio \"{args.portfolio_name}\" created")
            return portfolio

def main():
    parser = argparse.ArgumentParser(description="Calculate interest per second for a portfolio")
    parser.add_argument("-p", "--portfolio_file", type=str, help="File name of the serialized Portfolio object")
    parser.add_argument("portfolio_name", type=str, help="Name of the portfolio")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")

    args = parser.parse_args()
    p(args, "initializing portfolio")
    portfolio = initialize_portfolio(args)
    p(args, "starting session")
    session = PromptSession()
    p(args, "starting input loop")
    while True:
        action = session.prompt(f"[{portfolio.get_name()}] Choose an action: (a)dd loan, (r)emove loan, (s)how loans, (t)icker, (q)uit: ")
        p(args, f"user entered {action}")
        if action.lower() == "a":
            a(session, portfolio, args)
        elif action.lower() == "r":
            loan_name = session.prompt("Enter the name of the loan: ")
            r(portfolio, loan_name)
        elif action.lower() == "s":
            s(portfolio)
        elif action.lower() == "t":
            try:
                t(session, portfolio)
            except KeyboardInterrupt:
                curses.endwin()
                print("Ticker stopped")
        elif action.lower() == "q":
            q(portfolio, args)
            break
        else:
            print("Invalid action. Please try again.")


if __name__ == "__main__":
    main()

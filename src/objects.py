import pickle
from colorama import Fore

SECONDS_PER_YEAR = 60 * 60 * 24 * 365
DEFAULT_PATH = "./.portfolio"

class Loan:
    def __init__(self, principal: float, rate: float, name: str) -> None:
        self.principal = principal
        self.rate = rate
        self.interest_per_second = (self.rate / 100 / SECONDS_PER_YEAR) * principal
        self.name = name

    def __repr__(self) -> str:
        return f"Loan({self.principal}, {self.rate}, {self.name}, {self.interest_per_second})"
    
    def display(self, name_width:int = 20) -> str:
        interest_per_second = f"{Fore.LIGHTGREEN_EX}${format(self.interest_per_second, '.10f')}{Fore.RESET}"
        return f"\t{self.name:>{name_width}}: Principal: {Fore.LIGHTGREEN_EX}{'${:,.2f}'.format(self.principal):>11}{Fore.RESET}, Interest Rate: {Fore.LIGHTGREEN_EX}{'{:,.2f}'.format(self.rate):>5}%{Fore.RESET}, Interest/s: {interest_per_second}"
    
    def get_interest_per_second(self) -> float:
        return self.interest_per_second
    
    def get_principal(self) -> float:
        return self.principal
    
    def pay(self, amount: float) -> None:
        self.principal -= amount

class Portfolio:
    def __init__(self, name: str, path: str = "./.portfolio") -> None:
        self.loans = {}
        self.path = path
        self.name = name.strip().lower()

    def __repr__(self) -> str:
        return f"Portfolio({self.loans})"
    
    def add_loan(self, loan: Loan) -> None:
        if loan.name in self.loans.values():
            raise ValueError(f"A loan with the name {loan.name} already exists in the portfolio") 
        self.loans[loan.name] = loan

    def remove_loan(self, loan_name: str) -> None:
        if loan_name not in self.loans:
            raise ValueError(f"Loan {loan_name} not found in the portfolio")
        del self.loans[loan_name]

    def get_interest_per_second(self) -> float:
        if len(self.loans) == 0:
            return 0.0
        return sum(loan.get_interest_per_second() for loan in self.loans.values())
    
    def get_total_principal(self) -> float:
        if len(self.loans) == 0:
            return 0.0
        return sum(loan.get_principal() for loan in self.loans.values())

    def save_to_disk(self) -> None:
         with open(self.path, 'wb') as f:
            pickle.dump(self, f)

    def get_loans(self) -> dict[str, Loan]:
        return self.loans
    
    def get_name(self):
        return self.name
    
    def display_loans(self):
        print(f"\nTotal Principal: {Fore.LIGHTGREEN_EX}{'${:,.2f}'.format(self.get_total_principal()):>10}{Fore.RESET} @ {Fore.LIGHTGREEN_EX}${format(self.get_interest_per_second(), '.10f')}{Fore.RESET} $ per second:")
        if len(self.loans) == 0:
            print("No loans in the portfolio")
            return
        for loan in sorted(list(self.loans.values()), key=lambda x: x.interest_per_second, reverse=True):
            padding = max(len(loan.name) for loan in self.get_loans().values())
            print(loan.display(padding))
        print()

    @classmethod
    def load_from_disk(cls, path: str = DEFAULT_PATH) -> 'Portfolio':
        with open(path, "rb") as f:
            return pickle.load(f)

# Building Your Data File

When `finsim` runs, it searches for a JSON file containing the data to be used in the simulation. This file should be named `data.json` and stored in the root of this repository. 

This document will explain the expected layout and attributes of the `data.json` file. 

### Example File

An example of a full version of this file is [`data-example.json`](https://github.com/rhysb27/finsim/blob/master/data-example.json).

## File Root

`finsim` can be run in one of two modes - **single** or **group**:

* **single** - designed for use by a person aiming for a personal savings goal. For example, this could be a single person wishing to calculate how long it'll take them to save up for a car, or a person in a relationship looking to save for a personal purchase.
* **group** - designed primarily for use by a couple, aiming to for a joint savings goal, though works for groups of any number of people.

The simulation mode will be determined by the top level of the `data.json` file. It has two attributes:

```
{
  "people": [ Person ],
  "group": Group,
  "savings_goal": string?
}
```

* `people` (required) - a list of at least one **Person** objects.
* `group` - a **Group** object, required if `people` has a length of two or greater.
* `savings_goal` - `string` representing the overall savings target for the simulation. If not provided, the User Interface will prompt for the value during the simulation's initialisation. Must be greater than zero.

---

## Person

Each **Person** object represents an individual person's financial attributes.

```
{
  "name": string,
  "salary": Salary,
  "savings": [ Savings Account ],
  "expenses": Expenses,
  "debts": [ Debt ]?
}
```

* `name` (required) - the person's preferred name. Uniqueness is not a requirement but is highly recommended.
* `salary` (required) - a **Salary** object, representing this person's annual income, pension and payrise rate.
* `savings` (required) - a list of at least one **Savings Account** objects, each of which represents a savings account for which this person is personally responsible.
* `expenses` (required) - an **Expenses** object, representing this person's _individual_ expenses.
* `debts` - a list of **Debt** objects, each of which represents a debt for which this person is personally responsible.

---

## Group

The **Group** object is required when more than one **Person** object is defined, and represents the data tying each **Person** together.

```
{
  "expenses": Expenses,
  "proportional_expenses": boolean?
}
```

* `expenses` (required) - an **Expenses** object, representing the group's *shared* expenses.
* `proportional_expenses` - `true` or `false`, configures how shared expenses are divided among the group:
  * `true` : expenses are shared between each person in the group proportional to their salary.
  * `false` (default) : expenses are shared _equally_ between each person, regardless of salary differences.

---

## Salary

Each **Salary** object represents a person's payroll data. At the end of each simulated year, the program will simulate a payrise based either on the `payrise_rate` attribute (if provided) or the average rate of inflation.

```
{
  "base_salary": string,
  "pension": string?,
  "payrise_rate": string?
}
```

* `base_salary` (required) - `string` representing the person's gross annual salary (i.e. before deductions), e.g. `"18000"`. Must be greater than zero.
* `pension` - `string` representing the person's pension deduction rate, e.g. `"4.5"`. If present, must be ≥ zero. Defaults to `"0.0"`.
* `payrise_rate` - `string` representing the person's annual payrise rate. If present, must be ≥ zero. Defaults to the average rate of inflation.

---

## Expenses

Each **Expenses** object represents a collection of _monthly_ and _annual_ expenses.

```
{
  "monthly": [ Expense ]?,
  "annual": [ Expense ]?
}
```

* `monthly` - a list of Expense objects, representing monthly outgoings, such as rent, groceries and subscriptions.
* `annual` - a list of Expense objects, representing annual outgoings, such as an MOT or TV Licence. The simulation will divide the sum of all annual expenses by twelve, in order to form a consistent estimate for monthly outgoings.

---

## Expense

Each **Expense** object represents an individual expense. At the end of each simulated year, each expense will increase inline with the average rate of inflation, unless the `inflation` attribute is set to `false`.

```
{
  "name": string,
  "cost": string,
  "inflation": boolean?
}
```

* `name` (required) - `string` representing the expense's name. Used purely for ease of maintence of the data file by the user.
* `cost` (required) - `string` representing the cost of the expense. If the expense is annual, the per-year sum should be used - the program will divide them by twelve on the user's behalf. Must be greater than zero.
* `inflation` - `true` or `false`, dictates whether or not the expense is likely to increase each year.
  * `true` (default) : expense will be increased inline with the average rate of inflation at the end of each simulated year.
  * `false`: expense will remain fixed until the end of the simulation.

---

## Savings Account

Each **Savings Account** object represents an individual savings account. At the end of each simulated year, the account will earn interest based on the `interest_rate` attribute, if it is supplied.

```
{
  "name": string,
  "type": "traditional" | "lisa"?,
  "interest_rate": string?,
  "starting_balance": string?
}
```

* `name` (required) - `string` representing the account's name. Used by the User Interface for distinguishing between assets when prompting the user for payment strategies.
* `type` - `string` representing the type of account, which dictates any special behaviour. Currently only two types of savings account are supported:
  * `traditional` (default) : Traditional savings account with no special behaviour.
  * `lisa` : Lifetime ISA. Each deposit earns a 25% bonus, paid by the UK Government. Maximum deposit per tax year is £4000, though this is not yet enforced by the program.
* `interest_rate` - `string` representing the account's annual interest rate, e.g. `"1.25"` for a 1.25% annual interest rate. If supplied, this rate will be used to calculate interest at the end of each simulated year. Defaults to `"0.00"`.
* `starting_balance` - `string` representing the account's balance at the beginning of the simulation. Defaults to `"0.00"`.

---

## Debt

Each **Debt** object represents an individual debt. At the end of each simulated year, the account will accrue interest based on the `interest_rate` attribute, if it is supplied.

```
{
  "name": string,
  "starting_balance": string,
  "interest_rate": string?
}
```

* `name` (required) - `string` representing the debt's name. Used by the User Interface for distinguishing between liabilities when prompting the user for payment strategies.
* `starting_balance` (required) - `string` representing the debt's balance at the beginning of the simulation.
* `interest_rate` - `string` representing the account's annual interest rate, e.g. `"1.25"` for a 1.25% annual interest rate. If supplied, this rate will be used to calculate interest at the end of each simulated year. Defaults to `"0.00"`.


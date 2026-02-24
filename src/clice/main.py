from argparse import ArgumentParser
from random import randint
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Die:
    value:int

    def roll(self) -> int:
        return randint(1,self.value)

@dataclass
class DicePool:
    dice:list[Die] = field(default_factory=list)
    flat:int = 0
    groups:dict[int,int] = field(init=False)

    def __post_init__(self) -> None:
        groups = self._calculate_groups()
        object.__setattr__(self, "groups", groups)

    def _calculate_groups(self) -> dict[int,int]:
        values = [die.value for die in self.dice]
        values_set = sorted(set(values))
        return {val:values.count(val) for val in values_set}

    def add(self, *dice:Die) -> None:
        for die in dice:
            self.dice.append(die)

        self.dice.sort(key=lambda x:x.value)
        self.groups = self._calculate_groups()

    def _roll_single(self, verbose:bool) -> int:
        rolls = [die.roll() for die in self.dice]
        result = sum(rolls) + self.flat
        if verbose:
            print(f"{result} = {" ".join(str(result) for result in rolls)}" + (f" + {self.flat}" if self.flat > 0 else ""))
        return result
    
    def roll(self, times:int=1, verbose:bool=True) -> tuple[int, ...]:
        if verbose:
            message_die_part =' + '.join(f'{n}d{value}' for value, n in self.groups.items()) 
            print(f"total = {message_die_part}" + (f" + {self.flat}" if self.flat > 0 else ""))
        results = tuple(self._roll_single(verbose) for _ in range(times))
        return results
            
def parse_die(die:str) -> tuple[Die,...]:
    assert die.count("d") == 1
    d_idx = die.index("d")
    n_dice = int(die[:d_idx])
    value = int(die[d_idx+1:])
    return tuple([Die(value) for _ in range(n_dice)])

def parse_dice(dice:str) -> DicePool:
    parts = [part.strip().lower() for part in dice.split("+")]
    pool = DicePool()
    for part in parts:
        if "d" in part:
            pool.add(*parse_die(part))
        else:
            pool.flat += int(part)
    return pool
    

@dataclass
class RollArgs:
    dice:str
    dc:Optional[int]=None
    pool:DicePool=field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "pool", parse_dice(self.dice))

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="roll dice")
    parser.add_argument("dice", type=str, help="write here the dice you want to roll")
    parser.add_argument("-d","--dc", help="what is the dc", type=int)
    return parser

def parse_args(argv:list[str]|None=None) -> RollArgs:
    parser = build_parser()
    args = parser.parse_args(argv)
    return RollArgs(**vars(args))

def main(argv:list[str]|None=None) -> int:
    args = parse_args(argv)
    args.pool.roll(3, verbose=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

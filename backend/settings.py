from dataclasses import dataclass

@dataclass
class RuntimeSettings:
    reflectiveness: float = 0.6  # 0..1
    creativity: float = 0.4      # 0..1
    debug_meta: bool = False

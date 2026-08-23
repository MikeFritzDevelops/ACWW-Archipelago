from __future__ import annotations

from dataclasses import dataclass

from .memory_profiles import MemoryProfile, USA_REV_1_MEMORY


@dataclass(frozen=True)
class RomProfile:
    """Identity and memory layout for one supported ACWW ROM revision."""

    key: str
    display_name: str
    internal_title_prefix: bytes
    game_code: bytes
    revision: int
    memory: MemoryProfile
    outside_state_address: int
    bee_attack_data_address: int
    bee_sequence_address: int
    sha1_hashes: frozenset[str] = frozenset()

    def matches_header(
        self,
        internal_title: bytes,
        game_code: bytes,
        revision: int,
    ) -> bool:
        return (
            game_code == self.game_code
            and revision == self.revision
            and internal_title.startswith(self.internal_title_prefix)
        )


USA_REV_1 = RomProfile(
    key="usa_rev_1",
    display_name="Animal Crossing: Wild World (USA) (Rev 1)",
    internal_title_prefix=b"ANIMAL",
    game_code=b"ADME",
    revision=1,
    memory=USA_REV_1_MEMORY,
    outside_state_address=0x0E416C,
    bee_attack_data_address=0x259558,
    bee_sequence_address=0x2595A5,
    sha1_hashes=frozenset({
        "77FDE3E30E1E6068395D1F96EA63BE569B61C351",
    }),
)


ROM_PROFILES: tuple[RomProfile, ...] = (
    USA_REV_1,
)


def identify_rom_profile(
    internal_title: bytes,
    game_code: bytes,
    revision: int,
) -> RomProfile | None:
    """Return the supported profile matching an NDS header."""
    for profile in ROM_PROFILES:
        if profile.matches_header(
            internal_title,
            game_code,
            revision,
        ):
            return profile

    return None

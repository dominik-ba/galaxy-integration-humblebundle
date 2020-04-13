import pytest
import os
from pathlib import Path

from local import AppFinder
from consts import IS_WINDOWS


# unit

@pytest.fixture
def candidates():
    return set(
        ['Dummy', 'Trine 2: Complete Story', 'Space Pilgrim Episode III: Delta Pavonis', 'Halcyon 6: LIGHTSPEED EDITION', 'Shank 2', 'AaaaaAAaaaAAAaaAAAAaAAAAA!!! for the Awesome', "D4: Dark Dreams Don't Die - Season One", 'The Warlock of Firetop Mountain', 'Neon Chrome', 'Dustforce DX', 'RIVE: Wreck, Hack, Die, Retry', 'Samorost 3', 'World Of Goo', 'The Purring Quest', 'Trine Enhanced Edition', 'Kill The Bad Guy', 'Insanely Twisted Shadow Planet', 'Hustle Cat', 'Antichamber', 'Nihilumbra', 'The Fall Part 2: Unbound', 'FarSky', 'Race the Sun', 'Outlast: Whistleblower', 'Orwell: Ignorance is Strength', 'Lifeless Planet Premier Edition', 'Joe Danger 2: The Movie', 'A Fistful of Gun', 'The Count Lucanor', 'Dreamfall Chapters', 'Screencheat', 'HunieCam Studio', 'A Bird Story', 'Woten', 'To the Moon Minisode 2', 'Super Hexagon', 'Space Pilgrim Episode I: Alpha Centauri', "Broken Sword 5: The Serpent's Curse", 'The Inner World', 'Lakeview Cabin Collection', 'OlliOlli', 'Mini Metro', 'Hektor', 'Blocks That Matter', 'Dungeon Souls', 'Silence of the Sleep', 'Dead Synchronicity: Tomorrow Comes Today', 'Shadow Warrior', 'The Inner World Special Content', 'Alpha Polaris: A Horror Adventure Game', 'Volgarr the Viking', 'Always Sometimes Monsters', 'The Dark Eye: Chains of Satinav', 'Decay: The Mare', 'Gods Will Be Watching', 'Psychonauts', 'FOTONICA', 'Dust: An Elysian Tail', 'Uplay Client (will download latest version)', 'Read Only Memories (Legacy)', 'FRACT OSC', 'Sunset', 'Titan Attacks!', 'Master Reboot', 'Orwell: Keeping an Eye on You', 'Grim Fandango Remastered', 'Fire!', 'Cibele', 'Dreaming Sarah', 'Hacknet', 'Rayman® Legends', 'Guacamelee! Gold Edition', 'Rain World', 'The Stanley Parable', 'Dungeons of Dredmor Complete', 'Soulless: Ray Of Hope', '2064: Read Only Memories', 'Crawl', 'Pony Island', 'Tattletail', 'Whispering Willows', 'Deponia: The Complete Journey', 'The Fall', 'Unrest', 'Jalopy', 'Beatbuddy: Tale of the Guardians', 'Hand of Fate', 'Dropsy', 'AudioSurf', 'Giana Sisters: Rise of the Owlverlord', 'Deadlight', 'Oceanhorn: Monster of Uncharted Seas', 'The Silent Age', 'Her Story', 'Haven Moon - DRM free', 'Zen Bound 2', 'RONIN', 'BIT.TRIP Presents... Runner2: Future Legend of Rhythm Alien', 'Skullgirls', 'Armageddon Empires', 'Superbrothers: Sword & Sworcery EP', 'NOT A HERO', 'Giana Sisters: Twisted Dreams', 'Space Pilgrim Episode II: Epsilon Indi', 'VVVVVV', 'Trine', 'Outlast', 'A Story About My Uncle', 'Memoria', 'Kentucky Route Zero: PC Edition', 'LIMBO', 'Duke Grabowski, Mighty Swashbuckler', 'Puddle', 'MISSING: An Interactive Thriller - Episode One', 'Saints Row IV', '1954 Alcatraz', 'Rakuen', 'The Bridge', "The Beginner's Guide", 'To the Moon Minisode 1', 'Tokyo 42', 'Human Resource Machine', 'Puzzle Agent 2', 'Space Pilgrim Episode IV: Sol', 'Retro City Rampage DX', 'The Franz Kafka Videogame', 'Osmos', '12 is Better Than 6 DRM-free build', 'Samorost 2', 'The Whispered World Special Edition', 'Roundabout', 'Crimsonland', 'Darkout', 'Satellite Reign', 'Legend of Grimrock 2', 'Botanicula', 'To the Moon', 'Tower of Guns', 'Papo & Yo', 'Race the Sun - Sunrise', 'This War of Mine', 'TIS-100', 'Hacknet Labyrinths', "Hatoful Boyfriend Collector's Edition", 'Super Meat Boy', 'Brütal Legend', 'Dear Esther', 'OlliOlli2: Welcome to Olliwood', 'The Journey Down: Chapter Two', 'Undertale', 'Neverending Nightmares', 'FEZ', 'Tetrobot and Co.']
    )


@pytest.mark.parametrize('dirname, expected', [
    ('Dummy', ['Dummy']),
    ('Haven Moon - DRM free', ['Haven Moon - DRM free']),
])
def test_get_close_matches_exact(dirname, expected, candidates):
    result = AppFinder().get_close_matches(dirname, candidates, similarity=1)
    assert expected == result


@pytest.mark.parametrize('dirname, expected', [
    ('Dummy', ['Dummy']),
    ('Trine 2 Complete Story', ['Trine 2: Complete Story']),
])
def test_get_close_matches_close(dirname, expected, candidates):
    result = AppFinder().get_close_matches(dirname, candidates, similarity=0.8)
    assert expected == result


# integration

@pytest.fixture
def create_mock_walk(mocker):
    def fn(walk_paths: list):
        """ Creates mock of os.walk that is a bit more inteligent than simple return_value = iter(...)
        Also patch Path exists to True
        paths - expected os.walk result as a list of tuples
        """
        mocker.patch.object(Path, 'exists', return_value=True)
        mock_walk = mocker.patch('os.walk')
        def side_effect(_):
            """self reseting generator"""
            counter = 0
            while True:
                try:
                    yield walk_paths[counter]
                    counter += 1
                except IndexError:
                    counter = 0
                    return
        mock_walk.side_effect = side_effect
        return mock_walk
    return fn


@pytest.mark.skipif(not IS_WINDOWS, reason="windows case")
@pytest.mark.asyncio
async def test_scan_folder_windows(create_mock_walk):
    root = 'C:\\Program Files (x86)'
    paths = [
        (root, ('Samorost2', 'Shelter'), ()),
        (root + os.sep + 'Samorost2', ('01intro', '02pokop'), ('Samorost2.exe', 'Samorost2.ico')),
        (root + os.sep + 'Shelter', ('bin', 'assets'), ('Shelter.exe', 'README.txt'))
    ]
    create_mock_walk(paths)

    owned_games = {'Shelter'}
    result = await AppFinder()._scan_folders([root], owned_games)
    assert {'Shelter': Path(root) / 'Shelter' / 'Shelter.exe'} == result

    owned_games = {'Samorost 2'}
    result = await AppFinder()._scan_folders([root], owned_games)
    assert {'Samorost 2': Path(root) / 'Samorost2' / 'Samorost2.exe'} == result

    owned_games = {'Samorost 2', 'Shelter'}
    assert {
        'Samorost 2': Path(root) / 'Samorost2' / 'Samorost2.exe',
        'Shelter': Path(root) / 'Shelter' / 'Shelter.exe'
    } == await AppFinder()._scan_folders([root], owned_games)

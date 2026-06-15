from datetime import datetime
from pathlib import Path

import os
import pytest
import re
import tempfile

from worker.helpers import (
    get_files_from_location,
    parse_aoi_mek,
    parse_aleader_aoi,
    parse_stark_eol,
    parse_stark_eol_v2,
    parse_ziv_eol,
    parse_btf13,
    parse_fcl0022,
    parse_zurc,
    parse_btf_1177,
    parse_btf14,
    parse_bt81,
    parse_mil07,
    parse_dboard_r5,
    parse_lvs,
    parse_starktest_pc2,
    parse_automatic_label_check_01,
    parse_altra_air_lateral_uar260441,
    parse_btf06
)


class TestGetFilesFromLocation:
    def test_get_files_from_location(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(os.path.join(temp_dir, 'dir1'))
            os.makedirs(os.path.join(temp_dir, 'dir2', 'subdir'))
            os.makedirs(os.path.join(temp_dir, 'processed'))

            test_files = [
                os.path.join(temp_dir, 'file1.txt'),
                os.path.join(temp_dir, 'dir1', 'file2.txt'),
                os.path.join(temp_dir, 'dir2', 'file3.txt'),
                os.path.join(temp_dir, 'dir2', 'subdir', 'file4.txt'),
                os.path.join(temp_dir, 'processed', 'file5.txt')
            ]

            for file_path in test_files:
                with open(file_path, 'w') as f:
                    f.write('test content')

            result = get_files_from_location(temp_dir)

            # Ficheiros esperados excluindo os ficheiros dentro de 'processed'
            expected_files = [
                os.path.join(temp_dir, 'file1.txt'),
                os.path.join(temp_dir, 'dir1', 'file2.txt'),
                os.path.join(temp_dir, 'dir2', 'file3.txt'),
                os.path.join(temp_dir, 'dir2', 'subdir', 'file4.txt')
            ]

            assert sorted(result) == sorted(expected_files)

    def test_get_files_from_location_empty_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_files_from_location(temp_dir)
            assert result == []

    def test_get_files_from_location_nonexistent_dir(self):
        result = get_files_from_location('/nonexistent/directory')

        assert result == []


class TestParseAoiMek:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_mek' / 'logfile_ok.XML'

        result = parse_aoi_mek(logfile)

        assert result == {
            'serial_numbers': {
                '241201000600197510181': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 5, 5, 8, 10)
                }
            },
            'order': '2400002657',
            'side': 'TOP'
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_mek' / 'logfile_unit_nok.XML'

        result = parse_aoi_mek(logfile)

        assert result == {
            'serial_numbers': {
                '241201000600197510181': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 5, 5, 8, 10)
                }
            },
            'order': '2400002657',
            'side': 'TOP'
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_mek' / 'logfile_empty_serial_no.XML'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_aoi_mek(logfile)


class TestParseAoiALeader:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_aleader' / 'logfile_ok.CSV'

        result = parse_aleader_aoi(logfile)

        assert result == {
            'serial_numbers': {
                '4995211007500020107831': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 3, 12, 10, 58, 36)
                }
            },
            'children': [],
            'machine_id': '525',
            'order': '2500000783'
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_aleader' / 'logfile_unit_nok.CSV'

        result = parse_aleader_aoi(logfile)

        assert result == {
            'serial_numbers': {
                '4995211007500023107831': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 3, 12, 11, 00, 43)
                }
            },
            'children': [
                {'position': 3, 'status': 'NG'},
            ],
            'machine_id': '525',
            'order': '2500000783'
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'aoi_aleader' / 'logfile_empty_serial_no.CSV'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_aleader_aoi(logfile)


class TestEolStark:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_ok.xml'

        result = parse_stark_eol(logfile)

        assert result == {
            'serial_numbers': {
                'UT251902410034226': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 5, 9, 10, 10, 28)
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_unit_nok.XML'

        result = parse_stark_eol(logfile)

        assert result == {
            'serial_numbers': {
                'UT251902410033917': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 5, 15, 15, 13, 24)
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_empty_serial_no.XML'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_stark_eol(logfile)


class TestEolStarkV2:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_ok.json'

        result = parse_stark_eol_v2(logfile)

        assert result == {
            'serial_numbers': {
                '123456789': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 6, 16, 8, 19, 17)
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_unit_nok.json'

        result = parse_stark_eol_v2(logfile)

        assert result == {
            'serial_numbers': {
                '123456789': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 6, 16, 8, 19, 17)
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_stark' / 'logfile_empty_serial_no.json'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_stark_eol_v2(logfile)


class TestParseZivEol:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_ziv' / 'logfile_ok.csv'

        result = parse_ziv_eol(str(logfile))

        assert result == {
            'serial_numbers': {
                'AUA763722': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 7, 22, 12, 32, 37)
                }
            }
        }

    def test_logfile_unit_not_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_ziv' / 'logfile_unit_not_ok.csv'

        result = parse_ziv_eol(str(logfile))

        assert result == {
            'serial_numbers': {
                'AUA763722': {
                    'status': 'NOK',
                    'timestamp': datetime(2025, 7, 22, 12, 32, 37)
                }
            }
        }

    def test_logfile_timestamp_not_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_ziv' / 'logfile_timestamp_not_ok.csv'

        with pytest.raises(ValueError, match='"timestamp" must be a valid string in ISO-8601 format.'):
            parse_ziv_eol(str(logfile))

    def test_logfile_empty_serial_number(self):
        logfile = Path(__file__).parent / 'resources' / 'eol_ziv' / 'logfile_empty_serial_number.csv'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_ziv_eol(str(logfile))


class TestParseBTF13:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf13' / 'logfile_ok.XML'

        result = parse_btf13(logfile)

        assert result == {
            'serial_numbers': {
                'R02.252385.Y25F86.000103': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 7, 21, 12, 17, 8)
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf13' / 'logfile_unit_nok.XML'

        result = parse_btf13(logfile)

        assert result == {
            'serial_numbers': {
                'R02.252385.Y25F86.000103': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 7, 21, 12, 17, 8)
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'btf13' / 'logfile_empty_serial_no.XML'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_btf13(logfile)


class TestFCL0022:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'logfile_ok'

        result = parse_fcl0022(logfile)

        assert result == {
            'serial_numbers': {
                '978G01R04AUA763252': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 7, 22, 13, 53, 43)
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'logfile_unit_nok'

        result = parse_fcl0022(logfile)

        assert result == {
            'serial_numbers': {
                '978G01R04AUA763253': {
                    'status': 'NOK',
                    'timestamp': datetime(2025, 7, 23, 13, 53, 43)
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'logfile_empty_serial_no'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_fcl0022(logfile)

    def test_logfile_empty_timestamp(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'logfile_empty_TIMEEND'

        with pytest.raises(ValueError, match='"timestamp" must be a valid string in ISO-8601 format.'):
            parse_fcl0022(logfile)

    def test_logfile_empty_status(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'logfile_empty_BOARDRESULT'

        with pytest.raises(ValueError, match='BOARDRESULT is empty'):
            parse_fcl0022(logfile)

    def test_filename_ends_in_none(self):
        logfile = Path(__file__).parent / 'resources' / 'fcl0022' / 'filename_ends_in_NONE'
        result = parse_fcl0022(logfile)
        assert not result


class TestParseZurc:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'zurc' / 'logfile_ok.json'

        result = parse_zurc(logfile)

        assert result == {
            'serial_numbers': {
                '000041': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 5, 13, 11, 53, 39),
                    'lot_number': '251113'
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'zurc' / 'logfile_unit_nok.json'

        result = parse_zurc(logfile)

        assert result == {
            'serial_numbers': {
                '000041': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 5, 13, 11, 53, 39),
                    'lot_number': '251113'
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'zurc' / 'logfile_empty_serial_no.json'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_zurc(logfile)


class TestParseBTF1177:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf_1177' / 'logfile_ok.json'

        result = parse_btf_1177(logfile)

        assert result == {
            'serial_numbers': {
                '00000000000000039772@252903@0000000@8J-8F-EBXD46@27-08-25@1177 20-0188-227@R07': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 9, 4, 10, 6, 53),
                    'serial_no_2': 'ASX-001 04.09.25 0001 0233'
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf_1177' / 'logfile_unit_nok.json'

        result = parse_btf_1177(logfile)

        assert result == {
            'serial_numbers': {
                '00000000000000039772@252903@0000000@8J-8F-EBXD46@27-08-25@1177 20-0188-227@R07': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 9, 4, 10, 6, 53),
                    'serial_no_2': 'ASX-001 04.09.25 0001 0233'
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'btf_1177' / 'logfile_empty_serial_no.json'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_btf_1177(logfile)

    def test_logfile_empty_serial_no_2(self):
        logfile = Path(__file__).parent / 'resources' / 'btf_1177' / 'logfile_empty_serial_no_2.json'

        with pytest.raises(ValueError, match='serial_number_2 is empty'):
            parse_btf_1177(logfile)


class TestParseBTF14:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf14' / 'logfile_ok.xml'

        result = parse_btf14(logfile)

        assert result == {
            'serial_numbers': {
                'U004VIC': {
                    'status': 'OK',
                    'timestamp': datetime(2026, 5, 13, 15, 32, 54),
                    'tplaca': 'SMDAIQBOXDCVM_103',
                    'fwversion': 'AIRQBOXMAIN_V1.0.2_V1.0.7.s19'
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf14' / 'logfile_unit_nok.xml'

        result = parse_btf14(logfile)

        assert result == {
            'serial_numbers': {
                'U004VIC': {
                    'status': 'NG',
                    'timestamp': datetime(2026, 5, 13, 15, 32, 54),
                    'tplaca': 'SMDAIQBOXDCVM_103',
                    'fwversion': 'AIRQBOXMAIN_V1.0.2_V1.0.7.s19'
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'btf14' / 'logfile_empty_serial_no.xml'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_btf14(logfile)


class TestParseMil07:
    def test_mil_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'mil07' / 'logfile_ok.txt'

        result = parse_mil07(logfile)

        assert result == {
            'serial_numbers': {
                '23037000300002442740': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 11, 18, 9, 17, 45)
                }
            }
        }

    def test_mil_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'mil07' / 'logfile_unit_nok.txt'

        result = parse_mil07(logfile)

        assert result == {
            'serial_numbers': {
                '23037000300002442740': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 11, 18, 9, 17, 45)
                }
            }
        }

    def test_mil_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'mil07' / 'logfile_empty_serial_no.txt'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_mil07(logfile)


class TestParseBT81:
    def test_bt81_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'bt81' / 'logfile_ok.xml'

        result = parse_bt81(logfile)

        assert result == {
            'serial_numbers': {
                '2417214486': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 9, 23, 16, 32, 10),
                    'serial_no_2': '020215102523250000000002806'
                }
            }
        }

    def test_bt81_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'bt81' / 'logfile_unit_nok.xml'

        result = parse_bt81(logfile)

        assert result == {
            'serial_numbers': {
                '2417214486': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 9, 23, 16, 32, 10),
                    'serial_no_2': '020215102523250000000002806'
                }
            }
        }

    def test_bt81_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'bt81' / 'logfile_empty_serial_no.xml'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_bt81(logfile)

    def test_bt81_logfile_empty_serial_no_2(self):
        logfile = Path(__file__).parent / 'resources' / 'bt81' / 'logfile_ok_empty_serial_no_2.xml'

        with pytest.raises(ValueError, match='serial number gbt is empty'):
            parse_bt81(logfile)

    def test_bt81_logfile_nok_empty_serial_no_2(self):
        logfile = Path(__file__).parent / 'resources' / 'bt81' / 'logfile_nok_empty_serial_no_2.xml'

        result = parse_bt81(logfile)

        assert result == {
            'serial_numbers': {
                '2417214486': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 9, 23, 16, 32, 10)
                }
            }
        }


class TestParseDboardR5:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'dboard_r5' / 'logfile_ok.xml'

        result = parse_dboard_r5(logfile)

        assert result == {
            'serial_numbers': {
                'DBOARD_R5-174-0495-D-250828000730F': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 10, 28, 16, 20, 46),
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'dboard_r5' / 'logfile_unit_nok.xml'

        result = parse_dboard_r5(logfile)

        assert result == {
            'serial_numbers': {
                'DBOARD_R5-174-0495-D-250828000730F': {
                    'status': 'NG',
                    'timestamp': datetime(2025, 10, 28, 16, 20, 46),
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'dboard_r5' / 'logfile_empty_serial_no.xml'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_dboard_r5(logfile)


class TestParseLvs:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'lvs' / 'logfile_ok.csv'

        result = parse_lvs(logfile)

        assert result == {
            'serial_numbers': {
                '941G01R03AUA799636': {
                    'status': 'OK',
                    'timestamp': datetime(2025, 10, 30, 9, 23, 42),
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'lvs' / 'logfile_unit_nok.csv'

        result = parse_lvs(logfile)

        assert result == {
            'serial_numbers': {
                '941G01R03AUA799636': {
                    'status': 'NOK',
                    'timestamp': datetime(2025, 10, 30, 9, 23, 42),
                }
            }
        }

    def test_logfile_empty_serial_no_part_1(self):
        logfile = Path(__file__).parent / 'resources' / 'lvs' / 'logfile_empty_serial_no_part_1.csv'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_lvs(logfile)

    def test_logfile_empty_serial_no_part_2(self):
        logfile = Path(__file__).parent / 'resources' / 'lvs' / 'logfile_empty_serial_no_part_2.csv'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_lvs(logfile)

    def test_logfile_empty_serial_no_part_3(self):
        logfile = Path(__file__).parent / 'resources' / 'lvs' / 'logfile_empty_serial_no_part_3.csv'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_lvs(logfile)


class TestParseStarktestPC2:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'starktest_pc2' / 'logfile_ok.json'

        result = parse_starktest_pc2(logfile)

        assert result == {
            'serial_numbers': {
                'UT260524046114578': {
                    'status': 'OK',
                    'timestamp': datetime(2026, 1, 31, 11, 36, 14)
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'starktest_pc2' / 'logfile_unit_nok.json'

        result = parse_starktest_pc2(logfile)

        assert result == {
            'serial_numbers': {
                'UT260524046114578': {
                    'status': 'NG',
                    'timestamp': datetime(2026, 1, 31, 11, 36, 20)
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'starktest_pc2' / 'logfile_empty_serial_no.json'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_starktest_pc2(logfile)


class TestParseAutomaticLabelCheck01:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'parse_automatic_label_check_01' / 'logfile_ok.xml'

        result = parse_automatic_label_check_01(logfile)

        assert result == {
            'serial_numbers': {
                '14EFCF012320480B 03-95-731 26/12': {
                    'status': 'OK',
                    'timestamp': datetime(2026, 3, 26, 10, 19, 54),
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'parse_automatic_label_check_01' / 'logfile_unit_nok.xml'

        result = parse_automatic_label_check_01(logfile)

        assert result == {
            'serial_numbers': {
                '14EFCF012320480B 03-95-731 26/12': {
                    'status': 'NG',
                    'timestamp': datetime(2026, 3, 26, 10, 19, 54),
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(
            __file__).parent / 'resources' / 'parse_automatic_label_check_01' / 'logfile_empty_serial_no.xml'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_automatic_label_check_01(logfile)


class TestParseAltraAirLateralUar260441:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'altra_air_lateral_uar260441' / 'logfile_ok.xml'

        result = parse_altra_air_lateral_uar260441(logfile)

        assert result == {
            'serial_numbers': {
                'U0050H5': {
                    'status': 'OK',
                    'timestamp': datetime(2026, 5, 20, 14, 51, 59),
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'altra_air_lateral_uar260441' / 'logfile_unit_nok.xml'

        result = parse_altra_air_lateral_uar260441(logfile)

        assert result == {
            'serial_numbers': {
                'U0050H5': {
                    'status': 'NG',
                    'timestamp': datetime(2026, 5, 20, 14, 51, 59),
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(
            __file__
        ).parent / 'resources' / 'altra_air_lateral_uar260441' / 'logfile_empty_serial_no.xml'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_altra_air_lateral_uar260441(logfile)


class TestParseBTF06:
    def test_logfile_ok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf06' / 'logfile_ok.json'

        result = parse_btf06(logfile)

        assert result == {
            'serial_numbers': {
                '45-E366C-00-07;20260309;1;7.01;000014121': {
                    'status': 'OK',
                    'timestamp': datetime(2026, 6, 2, 11, 22, 16),
                }
            }
        }

    def test_logfile_unit_nok(self):
        logfile = Path(__file__).parent / 'resources' / 'btf06' / 'logfile_unit_nok.json'

        result = parse_btf06(logfile)

        assert result == {
            'serial_numbers': {
                '45-E366C-00-07;20260309;1;7.01;000014121': {
                    'status': 'NG',
                    'timestamp': datetime(2026, 6, 1, 11, 20, 16),
                }
            }
        }

    def test_logfile_empty_serial_no(self):
        logfile = Path(__file__).parent / 'resources' / 'btf06' / 'logfile_empty_serial_no.json'

        with pytest.raises(ValueError, match='serial number is empty'):
            parse_btf06(logfile)

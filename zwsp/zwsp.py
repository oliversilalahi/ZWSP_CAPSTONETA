# Mode operasi yang digunakan untuk menentukan karakter zero-width mana yang digunakan
MODE_ZWSP = 0  # Mode menggunakan 3 karakter zero-width
MODE_FULL = 1  # Mode menggunakan 5 karakter zero-width

# Unicode karakter zero-width
ZERO_WIDTH_SPACE = '\u200b'         # Zero-width space
ZERO_WIDTH_NON_JOINER = '\u200c'    # Zero-width non-joiner
ZERO_WIDTH_JOINER = '\u200d'        # Zero-width joiner
LEFT_TO_RIGHT_MARK = '\u200e'       # Left-to-right mark
RIGHT_TO_LEFT_MARK = '\u200f'       # Right-to-left mark

# Daftar unicode karakter zero-width jika mode yang dipilih MODE_ZWSP
list_ZWSP = [
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_NON_JOINER,
    ZERO_WIDTH_JOINER,
]
# Daftar unicode karakter zero-width jika mode yang dipilih MODE_FULL
list_FULL = [
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_NON_JOINER,
    ZERO_WIDTH_JOINER,
    LEFT_TO_RIGHT_MARK,
    RIGHT_TO_LEFT_MARK,
]


def get_padding_len(mode):
    """
    Mengembalikan panjang padding berdasarkan mode.

    Parameters:
    mode (int): Mode operasi (0 untuk MODE_ZWSP, 1 untuk MODE_FULL).

    Returns:
    int: Panjang padding (11 untuk MODE_ZWSP, 7 untuk MODE_FULL).
    """
    return 11 if mode == MODE_ZWSP else 7


def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyz'):
    """
    Mengubah bilangan desimal menjadi bilangan berbasis `b`.

    Parameters:
    num (int): Bilangan desimal yang akan diubah.
    b (int): Basis yang diinginkan.
    numerals (str): Karakter yang digunakan untuk basis.

    Returns:
    str: Bilangan dalam bentuk string berbasis `b`.

    Catatan:
    Fungsi ini menggunakan rekursi untuk mengubah bilangan desimal menjadi bentuk
    string berbasis `b`.
    """
    # Jika num adalah 0, maka num == 0 akan menghasilkan True dan mengembalikan numerals[0] (yaitu '0').
    # Jika num bukan 0, maka bagian ini akan menghasilkan False, sehingga eksekusi berlanjut ke bagian setelah or
    # Bagian `to_base(num // b, b, numerals)` ini memanggil fungsi to_base dengan num yang dibagi dengan b (num // b). Ini mengurangi nilai num secara rekursif hingga mencapai 0.
    # Rekursi ini bertujuan untuk membangun hasil konversi dari digit paling signifikan ke digit paling tidak signifikan.
    # Fungsi lstrip menghilangkan karakter '0' dari awal string yang dihasilkan oleh panggilan rekursif.
    # Ini memastikan bahwa tidak ada angka nol yang tidak diperlukan di awal hasil konversi.
    # pada `+ numerals[num % b]`. `num % b` mengambil sisa pembagian `num` dengan `b`, yang merupakan digit terakhir dalam basis yang diinginkan. Sehingga `numerals[num % b]` mengambil karakter yang sesuai dari numerals.
    return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def encode(msg, mode=MODE_FULL):
    """
    Menyandikan pesan teks menjadi karakter zero-width berdasarkan mode yang dipilih.

    Parameters:
    msg (str): Pesan teks yang akan disandikan.
    mode (int): Mode operasi (0 untuk MODE_ZWSP, 1 untuk MODE_FULL).

    Returns:
    str: Pesan yang telah disandikan dalam karakter zero-width.

    Raises:
    TypeError: Jika pesan yang diberikan bukan string.

    Penjelasan Teknis:
    Fungsi ini mengubah setiap karakter dalam pesan teks menjadi representasi angka berdasarkan
    panjang alfabet yang dipilih, kemudian menggantikan angka tersebut dengan karakter zero-width yang sesuai.
    """

    # Bagian ini memeriksa apakah `msg` adalah `string`. Jika bukan, akan mengeluarkan kesalahan `TypeError`
    if not isinstance(msg, str):
        raise TypeError('Cannot encode {0}'.format(type(msg).__name__))

    # Pilih alfabet berdasarkan mode
    # `alphabet` dipilih berdasarkan `mode`. Jika `mode` adalah `MODE_ZWSP`, maka alphabet adalah `list_ZWSP`, jika tidak, alphabet adalah `list_FULL`.
    alphabet = list_ZWSP if mode == MODE_ZWSP else list_FULL
    # Dapatkan panjang padding berdasarkan mode
    # `padding` ditentukan oleh fungsi `get_padding_len(mode)`, yang mengembalikan panjang padding yang sesuai untuk mode yang dipilih.
    padding = get_padding_len(mode)
    # Inisialisasi String yang Disandikan
    encoded = ''

    # Mengembalikan String Kosong jika Pesan Kosong
    if (len(msg) == 0):
        return ''

    # Mengkonversi Setiap Karakter dalam Pesan
    for msg_char in msg:
        # Ubah karakter menjadi kode berbasis panjang alfabet
        # `ord(msg_char)` mengubah karakter menjadi nilai ASCII-nya

        # `to_base(ord(msg_char), len(alphabet))` mengubah nilai ASCII menjadi representasi dalam basis yang ditentukan oleh panjang alphabet.
        # `'{0}{1}'.format('0' * padding, int(str(to_base(ord(msg_char), len(alphabet))))` menambahkan padding nol di depan hasil konversi.
        code = '{0}{1}'.format(
            '0' * padding, int(str(to_base(ord(msg_char), len(alphabet)))))

        # Mengambil bagian akhir dari `code` dengan panjang `padding`
        code = code[len(code) - padding:]
        # Mengganti Setiap Digit Kode dengan Karakter Zero-Width yang Sesuai
        for code_char in code:
            # Mengiterasi setiap karakter dalam `code`, mengonversi karakter tersebut ke indeks `int`.
            idx = int(code_char)
            # Menambahkan karakter zero-width yang sesuai dari `alphabet` ke string `encoded`.
            encoded = encoded+alphabet[idx]

    return encoded


def decode(msg, mode=MODE_FULL):
    """
    Mendekodekan pesan yang telah disandikan menjadi teks asli dan mengembalikan karakter non-zero-width asli.

    Parameters:
    msg (str): Pesan yang telah disandikan.
    mode (int): Mode operasi (0 untuk MODE_ZWSP, 1 untuk MODE_FULL).

    Returns:
    tuple: Teks asli yang telah didesandikan dan karakter non-zero-width asli.

    Raises:
    TypeError: Jika pesan yang diberikan bukan string atau jika encoding tidak diketahui terdeteksi.

    Penjelasan Teknis:
    Fungsi ini mengidentifikasi karakter zero-width dalam pesan yang diberikan dan mengubahnya kembali
    menjadi representasi angka, yang kemudian diubah menjadi karakter teks asli.
    """

    # Bagian ini memeriksa apakah `msg` adalah `string`. Jika bukan, akan mengeluarkan kesalahan `TypeError`
    if not isinstance(msg, str):
        raise TypeError('Cannot encode {0}'.format(type(msg).__name__))

    # Pilih alfabet berdasarkan mode
    # `alphabet` dipilih berdasarkan `mode`. Jika `mode` adalah `MODE_ZWSP`, maka `alphabet` adalah `list_ZWSP`, jika tidak, `alphabet` adalah `list_FULL`.
    alphabet = list_ZWSP if mode == MODE_ZWSP else list_FULL
    # Dapatkan panjang padding berdasarkan mode
    # `padding` ditentukan oleh fungsi` get_padding_len(mode)`, yang mengembalikan panjang `padding` yang sesuai untuk mode yang dipilih.
    padding = get_padding_len(mode)

    # Inisialisasi String yang Disandikan dan Teks yang Didekode

    encoded = ''
    decoded = ''
    original = ''

    # Bagian ini memeriksa setiap karakter dalam pesan msg dan memisahkan karakter zero-width dan karakter asli
    for msg_char in msg:
        # Jika karakter tersebut ada di `alphabet`, ia menambahkan indeks karakter tersebut ke `encoded`.
        if msg_char in alphabet:
            encoded = encoded + str(alphabet.index(msg_char))
        # Jika tidak, ia menambahkan karakter tersebut ke `original`.
        else:
            original = original+msg_char

    # Bagian ini memeriksa apakah panjang `encoded` adalah kelipatan dari `padding`.
    # Jika tidak, ia mengeluarkan kesalahan `TypeError` karena mendeteksi encoding yang tidak diketahui
    if (len(encoded) % padding != 0):
        raise TypeError('Unknown encoding detected!')

    # Decode setiap karakter yang disandikan
    # Fungsi ini menginisialisasi `cur_encoded_char` sebagai string kosong.
    cur_encoded_char = ''
    for idx, encoded_char in enumerate(encoded):
        # Untuk setiap karakter dalam `encoded`, ia menambahkannya ke `cur_encoded_char`.
        cur_encoded_char = cur_encoded_char + encoded_char

        # Jika indeks saat ini + 1 adalah kelipatan dari `padding`, ia mengonversi `cur_encoded_char` ke nilai ASCII menggunakan` int(cur_encoded_char, len(alphabet))`, kemudian mengonversi nilai ASCII tersebut ke karakter menggunakan `chr()`.
        if idx > 0 and (idx + 1) % padding == 0:
            # Karakter yang didekode ditambahkan ke `decoded`.
            decoded = decoded + chr(int(cur_encoded_char, len(alphabet)))
            cur_encoded_char = ''

    # Fungsi ini mengembalikan tuple yang terdiri dari pesan yang telah didekode (`decoded`) dan karakter asli (`original`).
    return (decoded, original)

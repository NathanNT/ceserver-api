# ceserver-api

A Python module for interfacing with Cheat Engine's `ceserver` (version 7.6) over the network. This project was created to enable remote memory scanning and manipulation by communicating directly with `ceserver`, a component of Cheat Engine designed to work with Android and Linux systems.

## 🚀 Features

- Connect to `ceserver` v7.6 remotely
- Send and receive commands in Cheat Engine’s custom protocol
- Perform memory operations (read/write/search) from Python

## 🔍 Background

This module is the result of a reverse engineering process aimed at understanding the `ceserver` protocol and replicating its functionality in Python.

Since the communication protocol used by `ceserver` is not officially documented, this project required extensive use of:

- 🧪 **Wireshark**: To capture and analyze packet data exchanged between Cheat Engine and `ceserver`.
- 🧠 **Reverse engineering**: To inspect the Cheat Engine source code and binaries to better understand how the communication protocol works.
- 🧰 **Hex editors & debugging tools**: For manually examining raw data structures and interactions.

The end goal is to provide a standalone Python library that can be used to interact with `ceserver` directly, for automation, scripting, or advanced memory analysis.

## 🛠️ Installation

<code>pip install ceserver-api</code>

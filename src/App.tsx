import { useEffect, useState } from 'react'
import { useIntMaxClient } from './hooks/useIntMaxClient'
import type { Token } from 'intmax2-client-sdk'
import { TokenType } from 'intmax2-client-sdk'

function App() {
  const {
    client,
    isLoggedIn,
    loading,
    error,
    initializeClient,
    login,
    logout,
  } = useIntMaxClient()

  const [balances, setBalances] = useState<any[]>([])
  const [receiver, setReceiver] = useState('')
  const [amount, setAmount] = useState('')
  const [transferResult, setTransferResult] = useState<string | null>(null)

  const [depositTokenAddress, setDepositTokenAddress] = useState('')
  const [depositAmount, setDepositAmount] = useState('')
  const [depositResult, setDepositResult] = useState<string | null>(null)

  const [withdrawTokenAddress, setWithdrawTokenAddress] = useState('')
  const [withdrawAmount, setWithdrawAmount] = useState('')
  const [withdrawResult, setWithdrawResult] = useState<string | null>(null)
  const [ethAddress, setEthAddress] = useState('')

  useEffect(() => {
    const fetchBalances = async () => {
      if (client && isLoggedIn) {
        try {
          const result = await client.fetchTokenBalances()
          setBalances(result.balances || [])
        } catch (err) {
          console.error('Error fetching balances:', err)
        }
      }
    }

    fetchBalances()
  }, [client, isLoggedIn])

  const handleTransfer = async () => {
    if (!client || !receiver || !amount) {
      alert('Please enter both a recipient address and an amount.')
      return
    }

    try {
      const baseToken = balances.find((b) => b.token.tokenIndex === 0)?.token
      if (!baseToken) {
        alert('Native token not found.')
        return
      }

      const nativeToken: Token = {
        tokenIndex: baseToken.tokenIndex,
        symbol: baseToken.symbol || 'INTMAX',
        decimals: baseToken.decimals || 18,
        contractAddress:
          baseToken.contractAddress ||
          '0x0000000000000000000000000000000000000000',
        tokenType: TokenType.NATIVE,
        price: 0,
      }

      await client.broadcastTransaction(
        [
          {
            address: receiver,
            amount: Number(amount),
            token: nativeToken,
          },
        ],
        false
      )

      setTransferResult('✅ Transfer successful!')
    } catch (err: any) {
      console.error('Transfer error:', err)
      setTransferResult(`❌ Transfer failed: ${err.message || err}`)
    }
  }

  const handleDeposit = async () => {
    if (!client || !depositTokenAddress || !depositAmount) {
      alert('Please fill in both token address and amount.')
      return
    }

    try {
      const amountForSdk = parseFloat(depositAmount)

      if (Number.isNaN(amountForSdk)) {
        alert('❌ Invalid deposit amount.')
        return
      }

      const matchedToken = balances.find(
        (b) =>
          b.token.contractAddress?.toLowerCase() ===
          depositTokenAddress.toLowerCase()
      )?.token

      if (!matchedToken) {
        alert('Token not found in balances.')
        return
      }

      const result = await client.deposit({
        token: matchedToken,
        amount: amountForSdk,
        address: client.address,
      })

      console.log('Deposit response:', result)
      setDepositResult('✅ Deposit successful! Check your balance soon.')
    } catch (err: any) {
      console.error('Deposit error:', err)
      setDepositResult(`❌ Deposit failed: ${err.message || err}`)
    }
  }

  const handleWithdraw = async () => {
    if (!client || !withdrawTokenAddress || !withdrawAmount || !ethAddress) {
      alert('Please fill in all required fields.')
      return
    }

    try {
      const amountForSdk = parseFloat(withdrawAmount)

      if (Number.isNaN(amountForSdk)) {
        alert('❌ Invalid withdraw amount.')
        return
      }

      const matchedToken = balances.find(
        (b) =>
          b.token.contractAddress?.toLowerCase() ===
          withdrawTokenAddress.toLowerCase()
      )?.token

      if (!matchedToken) {
        alert('Token not found in balances.')
        return
      }

      const result = await client.withdraw({
        token: matchedToken,
        amount: amountForSdk,
        address: ethAddress as `0x${string}`,
      })

      console.log('Withdraw response:', result)
      setWithdrawResult('✅ Withdraw successful! Check your L1 wallet.')
    } catch (err: any) {
      console.error('Withdraw error:', err)
      setWithdrawResult(`❌ Withdraw failed: ${err.message || err}`)
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>INTMAX Wallet Demo</h1>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {!client && <button onClick={initializeClient}>Initialize Client</button>}

      {client && !isLoggedIn && <button onClick={login}>Connect Wallet</button>}

      {client && isLoggedIn && (
        <div>
          <p>
            Connected Address: <code>{client.address}</code>
          </p>
          <button onClick={logout}>Logout</button>

          <div style={{ marginTop: '1rem' }}>
            <h3>Token Balances:</h3>
            {balances.length === 0 ? (
              <p>No tokens found.</p>
            ) : (
              <ul>
                {balances.map((b, index) => (
                  <li key={index} style={{ marginBottom: '0.5rem' }}>
                    <strong>{b.token.symbol || `Token #${b.token.tokenIndex}`}</strong>: {b.amount}
                    <span style={{ marginLeft: '1rem' }}>
                      💲Price: {b.token.price !== undefined ? `$${b.token.price}` : 'N/A'}
                    </span>
                    <button
                      style={{ marginLeft: '1rem' }}
                      onClick={() => {
                        const token = b.token
                        alert(`Token Info:\n- Symbol: ${token.symbol || 'N/A'}\n- Token Index: ${token.tokenIndex}\n- Contract Address: ${token.contractAddress || 'N/A'}\n- Decimals: ${token.decimals}\n- Token Type: ${token.tokenType}\n- Price: ${token.price !== undefined ? `$${token.price}` : 'N/A'}`)
                      }}
                    >
                      ℹ️
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* TRANSFER */}
          <div style={{ marginTop: '2rem' }}>
            <h3>Send Token</h3>
            <input type="text" placeholder="Recipient INTMAX address" value={receiver} onChange={(e) => setReceiver(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <input type="number" placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <button onClick={handleTransfer}>Send</button>
            {transferResult && <p style={{ marginTop: '1rem', color: transferResult.includes('successful') ? 'green' : 'red' }}>{transferResult}</p>}
          </div>

          {/* DEPOSIT */}
          <div style={{ marginTop: '2rem' }}>
            <h3>Deposit to INTMAX</h3>
            <input type="text" placeholder="L1 Token Address (Sepolia)" value={depositTokenAddress} onChange={(e) => setDepositTokenAddress(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <input type="number" placeholder="Amount to Deposit" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <button onClick={handleDeposit}>Deposit</button>
            {depositResult && <p style={{ marginTop: '1rem', color: depositResult.includes('successful') ? 'green' : 'red' }}>{depositResult}</p>}
          </div>

          {/* WITHDRAW */}
          <div style={{ marginTop: '2rem' }}>
            <h3>Withdraw from INTMAX</h3>
            <input type="text" placeholder="L1 Token Address (Sepolia)" value={withdrawTokenAddress} onChange={(e) => setWithdrawTokenAddress(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <input type="number" placeholder="Amount to Withdraw" value={withdrawAmount} onChange={(e) => setWithdrawAmount(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <input type="text" placeholder="Ethereum (L1) Address" value={ethAddress} onChange={(e) => setEthAddress(e.target.value)} style={{ width: '100%', marginBottom: '0.5rem' }} />
            <button onClick={handleWithdraw}>Withdraw</button>
            {withdrawResult && <p style={{ marginTop: '1rem', color: withdrawResult.includes('successful') ? 'green' : 'red' }}>{withdrawResult}</p>}
          </div>
        </div>
      )}
    </div>
  )
}

export default App

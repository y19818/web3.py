Miner API
=========

.. py:module:: web3.geth.miner

The ``web3.geth.miner`` object exposes methods to interact with the RPC APIs under
the ``miner_`` namespace that are supported by the Geth client.


Methods
-------

The following methods are available on the ``web3.geth.miner`` namespace.


.. py:method:: GethMiner.makeDAG(number)

    * Delegates to ``miner_makeDag`` RPC Method

    Generate the DAG for the given block number.

    .. code-block:: python

        >>> web3.geth.miner.makeDag(10000)


.. py:method:: GethMiner.setExtra(extra)

    * Delegates to ``miner_setExtra`` RPC Method

    Set the 32 byte value ``extra`` as the extra data that will be included
    when this node mines a block.

    .. code-block:: python

        >>> web3.geth.miner.setExtra('abcdefghijklmnopqrstuvwxyzABCDEF')


.. py:method:: GethMiner.setGasPrice(gas_price)

    * Delegates to ``miner_setGasPrice`` RPC Method

    Sets the minimum accepted gas price that this node will accept when mining
    transactions.  Any transactions with a gas price below this value will be
    ignored.

    .. code-block:: python

        >>> web3.geth.miner.setGasPrice(19999999999)


.. py:method:: GethMiner.start(num_threads)

    * Delegates to ``miner_start`` RPC Method

    Start the CPU mining process using the given number of threads.

    .. code-block:: python

        >>> web3.geth.miner.start(2)


.. py:method:: GethMiner.stop()

    * Delegates to ``miner_stop`` RPC Method

    Stop the CPU mining operation

    .. code-block:: python

        >>> web3.geth.miner.stop()


.. py:method:: GethMiner.startAutoDAG()

    * Delegates to ``miner_startAutoDag`` RPC Method

    Enable automatic DAG generation.

    .. code-block:: python

        >>> web3.geth.miner.startAutoDAG()


.. py:method:: GethMiner.stopAutoDAG()

    * Delegates to ``miner_stopAutoDag`` RPC Method

    Disable automatic DAG generation.

    .. code-block:: python

        >>> web3.geth.miner.stopAutoDAG()

address = '0x7B2d74D4C65D5720Fb765adA374cc44a66928e08'
abi = '[{"inputs":[{"internalType":"address","name":"tokenAddress","type":"address"},{"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"name":"AssetNotFound","type":"error"},{"inputs":[{"internalType":"address","name":"tokenAddress","type":"address"},{"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"name":"DuplicatedAsset","type":"error"},{"inputs":[{"internalType":"uint8","name":"sizeLimit","type":"uint8"}],"name":"ExceededStorageLimit","type":"error"},{"inputs":[],"name":"InconsistentBlockNumber","type":"error"},{"inputs":[],"name":"InvalidDataSigner","type":"error"},{"inputs":[],"name":"InvalidObservationTimestamp","type":"error"},{"inputs":[],"name":"MalformedData","type":"error"},{"inputs":[],"name":"UnexpectedBatchID","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"AddedAccess","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"wallet","type":"address"}],"name":"AddedSigner","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenAddress","type":"address"},{"indexed":false,"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"name":"AssetAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"tokenAddress","type":"address"},{"indexed":false,"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"name":"AssetRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"leaderAddress","type":"address"}],"name":"AssetUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"RemovedAccess","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"wallet","type":"address"}],"name":"RemovedSigner","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract OwnableInterface[]","name":"addresses","type":"address[]"}],"name":"acceptOwnerships","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"addAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenAddress","type":"address"},{"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"},{"internalType":"contract XAssetReadWriteInterface","name":"assetAddress","type":"address"}],"name":"addAsset","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"signingWallet","type":"address"}],"name":"addSigner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"batchId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getRecordsAtIndex","outputs":[{"components":[{"components":[{"internalType":"address","name":"symbol","type":"address"},{"internalType":"int192","name":"balance","type":"int192"},{"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"internalType":"struct XAssetInterface.AssetDetailRecord[]","name":"records","type":"tuple[]"},{"internalType":"uint64","name":"blockNumber","type":"uint64"}],"internalType":"struct XAssetInterface.BatchAssetRecord","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"hasAccess","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"signingWallet","type":"address"}],"name":"isSignerValid","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"removeAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenAddress","type":"address"},{"internalType":"enum XAssetInterface.AssetType","name":"assetType","type":"uint8"}],"name":"removeAsset","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"signingWallet","type":"address"}],"name":"removeSigner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"batchId_","type":"uint256"},{"internalType":"bytes","name":"message_","type":"bytes"},{"internalType":"bytes","name":"signature_","type":"bytes"}],"name":"updateAssets","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
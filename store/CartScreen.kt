package com.nandakaryana.store.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nandakaryana.store.Product
import com.nandakaryana.store.StoreApi
import kotlinx.coroutines.launch

@Composable
fun CartScreen(storeApi: StoreApi, onCheckout: () -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    var cartItems by remember { mutableStateOf(listOf<Product>()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        try {
            val response = storeApi.getCart()
            // Parse response to list of products (implement parseCartItems)
            cartItems = parseCartItems(response)
        } catch (e: Exception) {
            errorMessage = "Failed to load cart"
        } finally {
            isLoading = false
        }
    }

    if (isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    } else if (errorMessage != null) {
        Text(text = errorMessage ?: "", color = MaterialTheme.colors.error)
    } else {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(cartItems) { item ->
                    Text(text = "${item.name} - Qty: ${item.quantity} - Price: ₹${item.price}")
                }
            }
            Button(
                onClick = onCheckout,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Checkout")
            }
        }
    }
}

// Placeholder for parsing cart items from response string
fun parseCartItems(response: String): List<Product> {
    // Implement JSON parsing here
    return emptyList()
}

package com.nandakaryana.store.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.rememberAsyncImagePainter
import com.nandakaryana.store.Product
import com.nandakaryana.store.StoreApi
import kotlinx.coroutines.launch

@Composable
fun ProductDetailsScreen(storeApi: StoreApi, product: Product, onAddToCart: () -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    var recommendedProducts by remember { mutableStateOf(listOf<Product>()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(product.id) {
        try {
            val response = storeApi.getRecommendedProducts(product.id)
            recommendedProducts = parseProducts(response)
        } catch (e: Exception) {
            errorMessage = "Failed to load recommendations"
        } finally {
            isLoading = false
        }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Image(
            painter = rememberAsyncImagePainter(product.image),
            contentDescription = product.name,
            modifier = Modifier
                .fillMaxWidth()
                .height(250.dp),
            contentScale = ContentScale.Crop
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(text = product.name, style = MaterialTheme.typography.h5)
        Text(text = product.quantity, style = MaterialTheme.typography.body2)
        Text(text = "₹${product.price}", style = MaterialTheme.typography.h6, modifier = Modifier.padding(vertical = 8.dp))
        Button(onClick = onAddToCart, modifier = Modifier.fillMaxWidth()) {
            Text("Add to Cart")
        }
        Spacer(modifier = Modifier.height(24.dp))
        Text(text = "Recommended Products", style = MaterialTheme.typography.h6)
        if (isLoading) {
            CircularProgressIndicator()
        } else if (errorMessage != null) {
            Text(text = errorMessage ?: "", color = MaterialTheme.colors.error)
        } else {
            LazyRow {
                items(recommendedProducts) { recProduct ->
                    Card(
                        modifier = Modifier
                            .width(150.dp)
                            .padding(8.dp)
                    ) {
                        Column(modifier = Modifier.padding(8.dp)) {
                            Image(
                                painter = rememberAsyncImagePainter(recProduct.image),
                                contentDescription = recProduct.name,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(100.dp),
                                contentScale = ContentScale.Crop
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(text = recProduct.name, style = MaterialTheme.typography.subtitle1)
                            Text(text = "₹${recProduct.price}", style = MaterialTheme.typography.subtitle2)
                        }
                    }
                }
            }
        }
    }
}

// Placeholder for parsing products from JSON string
fun parseProducts(jsonString: String): List<Product> {
    // Implement JSON parsing here or use a JSON library
    return emptyList()
}

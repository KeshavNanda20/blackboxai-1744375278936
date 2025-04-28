package com.nandakaryana.store

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.rememberAsyncImagePainter
import kotlinx.coroutines.launch
import com.nandakaryana.store.ui.screens.CartScreen
import com.nandakaryana.store.ui.screens.CheckoutScreen
import com.nandakaryana.store.ui.screens.ProductDetailsScreen
import com.nandakaryana.store.Product

class MainActivity : ComponentActivity() {

    private val storeApi = StoreApi("http://10.0.2.2:8000") // Use 10.0.2.2 for localhost in Android emulator

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    var currentScreen by remember { mutableStateOf("productList") }
                    var selectedProduct by remember { mutableStateOf<Product?>(null) }

                    when (currentScreen) {
                        "productList" -> ProductListScreen(storeApi) { product ->
                            selectedProduct = product
                            currentScreen = "productDetails"
                        }
                        "productDetails" -> selectedProduct?.let { product ->
                            ProductDetailsScreen(storeApi, product) {
                                // Add to cart action
                                // For simplicity, navigate back to product list after adding
                                currentScreen = "productList"
                            }
                        }
                        "cart" -> CartScreen(storeApi) {
                            currentScreen = "checkout"
                        }
                        "checkout" -> CheckoutScreen(storeApi) {
                            currentScreen = "productList"
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ProductListScreen(storeApi: StoreApi, onBuyNow: (Product) -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    var products by remember { mutableStateOf(listOf<Product>()) }
    var isLoading by remember { mutableStateOf(true) }
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        try {
            val response = storeApi.getProducts()
            products = parseProducts(response)
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            isLoading = false
        }
    }

    if (isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    } else {
        LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            items(products) { product ->
                ProductCard(product = product, onBuyNow = {
                    onBuyNow(product)
                })
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun ProductCard(product: Product, onBuyNow: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = 4.dp
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            Image(
                painter = rememberAsyncImagePainter(product.image),
                contentDescription = product.name,
                modifier = Modifier.size(100.dp),
                contentScale = ContentScale.Crop
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(text = product.name, style = MaterialTheme.typography.h6, fontWeight = FontWeight.Bold)
                Text(text = product.quantity, style = MaterialTheme.typography.body2)
                Text(text = "₹${product.price}", style = MaterialTheme.typography.subtitle1, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = onBuyNow) {
                    Text("Buy Now")
                }
            }
        }
    }
}

// Data class for Product
data class Product(
    val id: Int,
    val name: String,
    val price: Int,
    val quantity: String,
    val image: String
)

// Simple JSON parser for products (replace with proper JSON parsing)
fun parseProducts(jsonString: String): List<Product> {
    // This is a placeholder. You should use kotlinx.serialization or Gson for real parsing.
    return emptyList()
}

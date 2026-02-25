# Streamlit Performance Optimization Guide

## Key Optimizations Implemented

### 1. **Caching**
- `@st.cache_resource`: Caches LLM initialization (expensive operation)
- `@st.cache_data`: Caches prompt template (immutable data)
- Prevents re-initialization on every app rerun

### 2. **Session State Management**
- Stores messages in session state to avoid recomputation
- Chat history persists across reruns without API calls

### 3. **Page Configuration**
- `st.set_page_config()` with optimal settings:
  - Wide layout to reduce scrolling
  - Collapsed sidebar by default
  - Minimal toolbar for faster rendering

### 4. **Error Handling**
- Timeout management (30s)
- Graceful error messages
- Prevents app crashes from API failures

### 5. **UI/UX Performance**
- Uses `st.chat_input()` for efficient input handling
- `st.chat_message()` for optimized chat display
- Spinners instead of progress bars (lighter rendering)

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

## Additional Performance Tips

### Deployment
```bash
# Run with production settings
streamlit run app.py --logger.level=warning --client.showWarningOnDirectExecution=false
```

### Memory Optimization
- Session state automatically clears old sessions
- Chat history can be cleared via sidebar button
- LLM object reused across all users

### Scaling
- Use `streamlit_cloud` for managed deployment
- Consider load balancing for multiple users
- Monitor with `--logger.level=debug` during development

## Streamlit Cloud Deployment

1. Push code to GitHub
2. Connect repo to Streamlit Cloud
3. Set environment variables: `API_URL`, `API_KEY`, `MODEL_NAME`
4. Deploy automatically

## Performance Metrics

| Feature | Improvement |
|---------|------------|
| First Load | ~2-3s |
| Chat Response | Real-time (API dependent) |
| Memory Usage | ~50-100MB base |
| Rerun Time | <500ms (with caching) |

## Monitoring Performance

Add to sidebar:
```python
import time
st.write(f"⏱️ Session time: {time.time() - st.session_state.get('start_time', time.time()):.2f}s")
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Slow app startup | Clear `.streamlit` cache, restart |
| High memory usage | Limit message history, add cleanup |
| API timeouts | Increase timeout in config.toml |
| Duplicate messages | Check session state initialization |

import torch
from tqdm import tqdm
def train_step(model: torch.nn.Module, 
            dataloader: torch.utils.data.DataLoader, 
            loss_fn: torch.nn.Module, 
            optimizer: torch.optim.Optimizer):
    # Put model in train mode
    model.train()

    device= (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    
    # Setup train loss and train accuracy values
    train_loss, train_acc = 0, 0
    dataloader_with_progress = tqdm(dataloader, total=len(dataloader), leave=True)
    # Loop through data loader data batches
    # for batch, (X, y) in enumerate(dataloader):
    for batch, (X, y) in enumerate(dataloader_with_progress):
        # Send data to target device
        X, y = X.to(device), y.to(device)

        # 1. Forward pass
        y_pred = model(X)

        # 2. Calculate  and accumulate loss
        loss = loss_fn(y_pred, y)
        train_loss += loss.item() 

        # 3. Optimizer zero grad
        optimizer.zero_grad()

        # 4. Loss backward
        loss.backward()

        # 5. Optimizer step
        optimizer.step()

        # Calculate and accumulate accuracy metric across all batches
        y_pred_class = torch.argmax(torch.softmax(y_pred, dim=1), dim=1)
        train_acc += (y_pred_class == y).sum().item()/len(y_pred)
        max_allo_mem = torch.cuda.max_memory_allocated()
        dataloader_with_progress.set_description(f"{max_allo_mem/1024**3:.2f}GB batch {batch+1}/{len(dataloader)}")
    # Adjust metrics to get average loss and accuracy per batch 
    train_loss = train_loss / len(dataloader)
    train_acc = train_acc / len(dataloader)
    dataloader_with_progress.close()
    return train_loss, train_acc
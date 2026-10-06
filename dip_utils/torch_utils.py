"""
Training and testing loops for the NeuralNets chapter.

NeuralNets/mnist_linear.ipynb writes these loops out in full and walks through
them step by step. The later notebooks (mnist_conv, yale_conv) import them from
here rather than repeating them, just as arr_info moved to matrix_utils after
the numpy tutorial.

Compared to the version in mnist_linear, these
- take the loss function as an argument: F.nll_loss for a model whose forward
  ends in log_softmax, F.cross_entropy for a model that returns raw scores
  (logits), and
- return the losses and accuracy, so that a notebook can plot training curves.
"""

import time

import torch
import torch.nn.functional as F


def train(args, model, device, train_loader, optimizer, epoch, loss_fn=F.nll_loss):
    """
    One epoch of training: a pass through all of train_loader, one optimizer
    step per batch. Prints progress every args.log_interval batches.
    Returns the average training loss over the epoch.
    """
    starttime = time.time()
    model.train()
    loss_sum = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = loss_fn(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            seen, total = batch_idx * len(data), len(train_loader.dataset)
            percent = 100. * batch_idx / len(train_loader)
            print(f'Train Epoch: {epoch} [{seen}/{total} ({percent:.0f}%)]\tLoss: {loss.item():.6f}')
        loss_sum += loss.item()

    loss_avg = loss_sum / len(train_loader)  # loss is a per-batch mean, so average over batches

    print(f'\nTrain set: Average loss: {loss_avg:.4f} ({time.time() - starttime:.3f} sec)')

    return loss_avg


def test(args, model, device, test_loader, loss_fn=F.nll_loss):
    """
    Evaluate the model on all of test_loader without computing gradients.
    Returns (average loss per example, fraction classified correctly).
    """
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += loss_fn(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # index of the highest score
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    test_acc = correct / len(test_loader.dataset)

    total = len(test_loader.dataset)
    print(f'Test set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{total} ({100. * test_acc:.0f}%)\n')

    return test_loss, test_acc

#include "data_structures.h"

CtQueue::CtQueue(int qz): q_size(qz)
{
  front = rear = nullptr;
  items = 0;
}

CtQueue::~CtQueue()
{
  Node * temp;
  while (front != nullptr)
  {
    temp = front;
    front = front->next;
    delete temp;
  }
}

bool CtQueue::is_empty() const
{
  return items == 0;
}

bool CtQueue::is_full() const
{
  return items == q_size;
}

int CtQueue::count() const
{
  return items;
}

bool CtQueue::enqueue(const Item & item)
{
  if (is_full())
  {
    return false;
  }

  Node * add = new Node;
  add->item = item;
  add->next = nullptr;

  if (front == nullptr)
  {
    front = add;
  }
  else
  {
    rear->next = add;
  }

  items++;

  rear = add;
  return true;
}

bool CtQueue::dequeue(Item & item)
{
  if (is_empty())
  {
    return false;
  }

  Node * temp = front;
  front = front->next;
  item = temp->item;
  delete temp;
  items--;

  if (front == nullptr)
  {
    rear = nullptr;
  }

  return true;
}




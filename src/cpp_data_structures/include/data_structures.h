#pragma once

typedef int Item;

class CtQueue
{
private:
  struct Node
  {
    Item item;
    Node * next;
  };

  static constexpr int Q_SIZE = 10;
  Node * front;
  Node * rear;
  const int q_size;
  int items;

public:
  CtQueue(int qz = Q_SIZE);
  ~CtQueue();
  CtQueue(const CtQueue &) = delete;
  CtQueue & operator=(const CtQueue&) = delete;
  bool is_empty() const;
  bool is_full() const;
  int count() const;
  bool enqueue(const Item &);
  bool dequeue(Item &);
};


from torch.utils.data import Dataset, IterableDataset, DataLoader

class PolicyGradientRLDataset(Dataset):
    def __init__(
        self,
        data 
    ):
        self.data = data 

    def __len__(self):
        return len(self.data[2]) 

    def __getitem__(self, idx):
        state = self.data[0][idx]
        act = self.data[1][idx]
        adv = self.data[2][idx]
        rew = self.data[3][idx]
        logp = self.data[4][idx]

        return state, act, adv, rew, logp
    

class QPolicyGradientRLDataset(Dataset):
    def __init__(
        self,
        data
    ):
        self.data = data

    def __len__(self):
        return len(self.data[3])

    def __getitem__(self, idx):
        obs = self.data[0][idx]
        obs2 = self.data[1][idx]
        act = self.data[2][idx]
        rew = self.data[3][idx]
        done = self.data[4][idx]
        return obs, obs2, act, rew, done
